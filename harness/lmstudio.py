
import json
import os
import re
import shutil
from datetime import datetime, timezone
from itertools import chain, islice
from pathlib import Path

import httpx

from .util import now_ms, read_json, run_capped

LOAD_TIMEOUT_S = 900
UNLOAD_TIMEOUT_S = 120

SERVER_LOG_DIR = Path.home() / ".lmstudio" / "server-logs"
_REQ_MARK = "Received request: POST to /v1/chat/completions with body {"
_TS_LINE = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]")
_LOG_READ_CAP = 64 * 1024 * 1024


def lms_exe() -> str | None:
    p = shutil.which("lms")
    if p:
        return p
    cand = Path.home() / ".lmstudio" / "bin" / "lms.exe"
    return str(cand) if cand.exists() else None


def _api_root(base_url: str) -> str:
    base = (base_url or "http://localhost:1234/v1").rstrip("/")
    return base[:-3] if base.endswith("/v1") else base


def model_states(base_url: str, key_env: str | None = None) -> dict[str, str] | None:
    key = os.environ.get(key_env) if key_env else None
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    try:
        resp = httpx.get(f"{_api_root(base_url)}/api/v0/models",
                         headers=headers, timeout=3)
        if resp.status_code != 200:
            return None
        return {e["id"]: e.get("state", "not-loaded")
                for e in resp.json().get("data", [])
                if e.get("type") in ("llm", "vlm", None)}
    except (httpx.HTTPError, ValueError, KeyError):
        return None


def model_info(base_url: str, key_env: str | None, model_id: str) -> dict | None:
    key = os.environ.get(key_env) if key_env else None
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    try:
        resp = httpx.get(f"{_api_root(base_url)}/api/v0/models",
                         headers=headers, timeout=3)
        if resp.status_code != 200:
            return None
        for e in resp.json().get("data", []):
            if e.get("id") == model_id:
                return {k: e.get(k) for k in
                        ("quantization", "arch", "max_context_length",
                         "compatibility_type", "publisher")}
    except (httpx.HTTPError, ValueError):
        pass
    return None


def unload_all(progress=print) -> bool:
    exe = lms_exe()
    if not exe:
        return False
    proc = run_capped([exe, "unload", "--all"], UNLOAD_TIMEOUT_S,
                      text=True, encoding="utf-8", errors="replace")
    if proc.timed_out:
        progress("lms unload --all timed out")
        return False
    if proc.returncode != 0:
        progress(f"lms unload failed: {(proc.stderr or proc.stdout).strip()[:200]}")
        return False
    return True


def load_model(model_id: str, progress=print,
               context_length: int = 0, gpu_offload: str = "max") -> float | None:
    exe = lms_exe()
    if not exe:
        return None
    cmd = [exe, "load", model_id, "--yes"]
    if context_length:
        cmd += ["--context-length", str(context_length)]
    if gpu_offload and gpu_offload != "auto":
        cmd += ["--gpu", gpu_offload]
    t0 = now_ms()
    proc = run_capped(cmd, LOAD_TIMEOUT_S,
                      text=True, encoding="utf-8", errors="replace")
    if proc.timed_out:
        progress(f"lms load {model_id} timed out after {LOAD_TIMEOUT_S}s")
        return None
    if proc.returncode != 0:
        progress(f"lms load failed: {(proc.stderr or proc.stdout).strip()[:200]}")
        return None
    return now_ms() - t0


def received_requests(days: set[str] | None = None) -> list[dict]:
    out: list[dict] = []
    if not SERVER_LOG_DIR.is_dir():
        return out
    for path in sorted(SERVER_LOG_DIR.glob("*/*.log")):
        day = path.name.split(".")[0]
        if days is not None and day not in days:
            continue
        try:
            if path.stat().st_size > _LOG_READ_CAP:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        for i, head in enumerate(lines):
            at = head.find(_REQ_MARK)
            if at < 0:
                continue
            m = _TS_LINE.match(head[:at])
            if not m:
                continue
            depth, buf = 1, ["{"]
            for line in chain([head[at + len(_REQ_MARK):]],
                              islice(lines, i + 1, None)):
                if _TS_LINE.match(line):
                    depth = -1
                    break
                buf.append(line)
                depth += line.count("{") - line.count("}")
                if depth <= 0:
                    break
            if depth != 0:
                continue
            try:
                body = json.loads("\n".join(buf))
            except ValueError:
                continue
            out.append({"ts": datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S"),
                        "model": str(body.get("model") or ""), "body": body})
    return out


_SAMPLING_KEYS_SEEN = ("temperature", "top_p", "top_k", "min_p", "top_a", "seed",
                       "repetition_penalty", "presence_penalty",
                       "frequency_penalty")


def _num_eq(a, b) -> bool:
    if a is None or b is None:
        return a is b
    try:
        return abs(float(a) - float(b)) < 1e-9
    except (TypeError, ValueError):
        return a == b


def _match(expected: dict, body: dict) -> list[str]:
    diffs = []
    for k, v in (expected or {}).items():
        if k not in body:
            diffs.append(f"{k}: sent {v}, NOT RECEIVED")
        elif not _num_eq(v, body[k]):
            diffs.append(f"{k}: sent {v}, received {body[k]}")
    for k in _SAMPLING_KEYS_SEEN:
        if k in body and k not in (expected or {}):
            diffs.append(f"{k}: received {body[k]} but never sent — something "
                         f"else is injecting it")
    return diffs


def _sampling_fingerprint(runs_dir) -> str:
    parts = []
    if SERVER_LOG_DIR.is_dir():
        for p in sorted(SERVER_LOG_DIR.glob("*/*.log")):
            try:
                st = p.stat()
            except OSError:
                continue
            parts.append(f"{p.name}:{st.st_size}:{int(st.st_mtime)}")
    newest = 0.0
    n = 0
    if runs_dir.is_dir():
        for p in runs_dir.glob("*/*/*/metrics.json"):
            try:
                newest = max(newest, p.stat().st_mtime)
            except OSError:
                continue
            n += 1
    parts.append(f"runs:{n}:{int(newest)}")
    import hashlib
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:32]


def _sampling_cache_path():
    from . import config
    return config.ROOT / ".lmstudio-sampling.json"


def confirm_sampling(runs_dir=None, models=None) -> dict:
    from . import config
    canonical = runs_dir is None and models is None
    runs_dir = runs_dir or config.RUNS_DIR
    if not canonical:
        return _confirm_sampling_uncached(runs_dir, models)
    fp = _sampling_fingerprint(runs_dir)
    cache = read_json(_sampling_cache_path(), {}) or {}
    if cache.get("fingerprint") == fp:
        return cache.get("result") or {}
    out = _confirm_sampling_uncached(runs_dir, models)
    try:
        from .util import write_json
        write_json(_sampling_cache_path(), {"fingerprint": fp, "result": out})
    except OSError:
        pass
    return out


def _confirm_sampling_uncached(runs_dir, models=None) -> dict:
    from .registry import load_models
    models = models or load_models(include_disabled=True)
    local = {m.name for m in models if m.local}
    ids = {m.name: m.model for m in models if m.local}
    if not local or not runs_dir.is_dir():
        return {}

    cells = []
    days: set[str] = set()
    for mfile in sorted(runs_dir.glob("*/*/*/metrics.json")):
        if mfile.parents[1].name not in local:
            continue
        d = read_json(mfile, {})
        used = d.get("sampling_used")
        if used is None:
            continue
        for att in (d.get("attempts") or []):
            t = att.get("t_start")
            if not t:
                continue
            try:
                when = datetime.fromisoformat(t).astimezone().replace(tzinfo=None)
            except ValueError:
                continue
            days.add(when.strftime("%Y-%m-%d"))
            cells.append({"model": mfile.parents[1].name, "task": mfile.parent.name,
                          "when": when, "expected": {**used,
                                                     "max_tokens": d.get("max_tokens")
                                                     if d.get("max_tokens") else None}})
    if not cells:
        return {}
    for c in cells:
        c["expected"] = {k: v for k, v in c["expected"].items() if v is not None}

    logged = [r for r in received_requests(days) if r["model"]]
    by_model: dict[str, list] = {}
    for r in logged:
        by_model.setdefault(r["model"], []).append(r)
    for v in by_model.values():
        v.sort(key=lambda r: r["ts"])

    out: dict[str, dict] = {}
    for c in cells:
        slot = out.setdefault(c["model"], {"confirmed": 0, "mismatched": 0,
                                           "unlogged": 0, "total": 0,
                                           "details": []})
        slot["total"] += 1
        cand = [r for r in by_model.get(ids.get(c["model"], c["model"]), [])
                if -2 <= (r["ts"] - c["when"]).total_seconds() <= 120]
        if not cand:
            slot["unlogged"] += 1
            continue
        diffs = _match(c["expected"], cand[0]["body"])
        if diffs:
            slot["mismatched"] += 1
            slot["details"].append((c["task"], diffs))
        else:
            slot["confirmed"] += 1
    return out
