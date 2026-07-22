"""Model auto-registration.

    python -m harness add lmstudio          # register every model LM Studio serves
    python -m harness add claude [alias]    # register Claude via the CLI (sonnet/opus/haiku)

Writes one yaml per model into models/ and never overwrites an existing file.
"""

import os
import re
from pathlib import Path

import httpx

from . import config

LMSTUDIO_DEFAULT_URL = "http://localhost:1234/v1"
LMSTUDIO_KEY_ENV = "LMSTUDIO_API_KEY"

LMSTUDIO_TEMPLATE = """\
# Auto-registered from LM Studio by `harness add lmstudio`
name: {name}
provider: openai
base_url: {base_url}
model: {model_id}
key_env: {key_env}
local: true
stream: true
supports_tools: true          # set false if this model can't do tool calls (skips tier 2)
max_tokens: 32768   # uniform thinking budget across all local models (fairness)
temperature: 0.2
pricing: {{ input_per_mtok: 0, output_per_mtok: 0 }}
enabled: true
"""

CLAUDE_TEMPLATE = """\
# Auto-registered by `harness add claude` — runs on your subscription, no API key.
# Isolation: fresh `claude -p` subprocess per request, empty sandbox cwd, file/
# shell/web tools disallowed. The model cannot see tasks/, checkers, or history.
name: claude-cli-{alias}
provider: claude-cli
model: {model_id}
local: false
stream: false
supports_tools: false
max_tokens: 16384
temperature: 0.2
# API-equivalent pricing (actual billing is your subscription):
pricing: {{ input_per_mtok: {in_price}, output_per_mtok: {out_price} }}
enabled: {enabled}
"""

CLAUDE_PRICES = {"fable": (10.0, 50.0), "sonnet": (3.0, 15.0),
                 "opus": (5.0, 25.0), "haiku": (1.0, 5.0)}

CLAUDE_MODEL_IDS = {"fable": "claude-fable-5"}


def _slug(model_id: str) -> str:
    base = model_id.split("/")[-1]
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", base).strip("-").lower()


def add_lmstudio(base_url: str = LMSTUDIO_DEFAULT_URL, progress=print) -> list[Path]:
    key = os.environ.get(LMSTUDIO_KEY_ENV)
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    try:
        resp = httpx.get(f"{base_url.rstrip('/')}/models", headers=headers, timeout=10)
    except httpx.HTTPError as e:
        progress(f"error: cannot reach LM Studio at {base_url} — is the server started? ({e})")
        return []
    if resp.status_code == 401:
        progress(f"error: LM Studio wants an API key — set the {LMSTUDIO_KEY_ENV} env var "
                 "(or disable 'Require API key' in LM Studio's server settings).")
        return []
    if resp.status_code != 200:
        progress(f"error: LM Studio returned HTTP {resp.status_code}: {resp.text[:200]}")
        return []

    created: list[Path] = []
    for entry in resp.json().get("data", []):
        model_id = entry.get("id", "")
        if not model_id or "embed" in model_id.lower():
            continue
        name = _slug(model_id)
        path = config.MODELS_DIR / f"{name}.yaml"
        if path.exists():
            progress(f"  = {name}  (already registered, untouched)")
            continue
        path.write_text(LMSTUDIO_TEMPLATE.format(
            name=name, base_url=base_url, model_id=model_id,
            key_env=LMSTUDIO_KEY_ENV if key else "null"), encoding="utf-8")
        progress(f"  + {name}  ({model_id})")
        created.append(path)
    if not created:
        progress("  nothing new to register.")
    return created


def probe_models(models, probe_local: bool = True) -> dict[str, dict]:
    """Live availability per model, for the control panel. 2s timeouts, one
    round-trip per base_url. probe_local=False touches no network — locals
    report 'not probed'; cloud/CLI checks are instant env-var/PATH lookups."""
    import shutil
    server_cache: dict[str, list | None] = {}
    states_cache: dict[str, dict | None] = {}

    def server_ids(base_url: str, key_env: str | None):
        """Returns a list of model ids, or the string 'auth'/'offline'."""
        if base_url in server_cache:
            return server_cache[base_url]
        key = os.environ.get(key_env) if key_env else None
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        try:
            resp = httpx.get(f"{base_url.rstrip('/')}/models", headers=headers, timeout=2)
            if resp.status_code == 200:
                ids = [e.get("id") for e in resp.json().get("data", [])]
            elif resp.status_code in (401, 403):
                ids = "auth"
            else:
                ids = "offline"
        except (httpx.HTTPError, ValueError):
            ids = "offline"
        server_cache[base_url] = ids
        return ids

    out: dict[str, dict] = {}
    for m in models:
        if not m.enabled:
            out[m.name] = {"status": "disabled", "ok": False,
                           "detail": f"enabled: false in {m.source_file}"}
        elif m.provider == "claude-cli":
            ok = shutil.which("claude") is not None
            out[m.name] = {"status": "ready" if ok else "missing CLI", "ok": ok,
                           "detail": "runs on subscription via claude -p"}
        elif m.provider == "mock":
            out[m.name] = {"status": "ready", "ok": True, "detail": "offline mock"}
        elif m.local and not probe_local:
            out[m.name] = {"status": "not probed", "ok": False,
                           "detail": "open the Local section to query the server"}
        elif m.local:
            from .lmstudio import lms_exe, model_states
            burl = m.base_url or LMSTUDIO_DEFAULT_URL
            if burl not in states_cache:
                states_cache[burl] = model_states(burl, m.key_env)
            states = states_cache[burl]
            if states is not None:
                preload = "pre-loads via lms before run" if lms_exe() \
                    else "will JIT-load on first request"
                if m.model not in states:
                    out[m.name] = {"status": "not on server", "ok": False,
                                   "detail": "model not downloaded in LM Studio"}
                elif states[m.model] == "loaded":
                    out[m.name] = {"status": "loaded", "ok": True,
                                   "detail": "model active on server"}
                else:
                    out[m.name] = {"status": "downloaded", "ok": True,
                                   "detail": f"on disk — {preload}"}
                continue
            ids = server_ids(m.base_url or LMSTUDIO_DEFAULT_URL, m.key_env)
            if ids == "offline":
                out[m.name] = {"status": "server offline", "ok": False,
                               "detail": f"no response from {m.base_url}"}
            elif ids == "auth":
                out[m.name] = {"status": "auth failed", "ok": False,
                               "detail": f"server rejected key — check {m.key_env} / .env"}
            elif m.model in ids:
                out[m.name] = {"status": "loaded", "ok": True,
                               "detail": "model active on server"}
            else:
                out[m.name] = {"status": "not loaded", "ok": True,
                               "detail": "server up — will JIT-load on first request"}
        else:
            has_key = bool(m.api_key) or not m.key_env
            out[m.name] = {"status": "key set" if has_key else "no API key",
                           "ok": has_key,
                           "detail": f"env var {m.key_env}" if m.key_env else "no key needed"}
    return out


def resolve_claude_alias(alias: str, timeout_s: int = 90) -> str | None:
    """Resolve a moving alias to the concrete id it lands on right now. `sonnet`
    is a pointer Anthropic can repoint; recording the pointer instead of the
    target breaks comparability over time, so we resolve once and pin the id.
    One trivial request; None if the CLI can't tell us."""
    import json as _json
    import shutil as _sh
    import subprocess as _sp

    exe = _sh.which("claude")
    if not exe:
        return None
    try:
        proc = _sp.run(
            [exe, "-p", "--output-format", "json", "--max-turns", "1",
             "--model", alias, "--disallowedTools",
             "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,Task"],
            input="hi", capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout_s)
        data = _json.loads(proc.stdout or "{}")
    except (_sp.TimeoutExpired, _json.JSONDecodeError, OSError, ValueError):
        return None
    from .adapters import _resolve_served_model
    return _resolve_served_model(data.get("modelUsage"), alias)


def claude_registration(alias: str) -> tuple[str, str]:
    """(concrete_model_id, registered_name) for a Claude alias or full id.
    Shared by add_claude and the /watch Scout button so they agree on what an
    alias becomes."""
    alias = _slug(alias.lower())
    concrete = CLAUDE_MODEL_IDS.get(alias) or resolve_claude_alias(alias) or alias
    label = _slug(concrete[len("claude-"):] if concrete.startswith("claude-")
                  else concrete)
    return concrete, f"claude-cli-{label}"


def add_claude(alias: str = "sonnet", progress=print,
               enabled: bool = True) -> Path | None:
    """Register a Claude model, pinned to the concrete version it resolves to,
    so the leaderboard never says "sonnet" while running something else."""
    concrete, name = claude_registration(alias)
    if concrete != _slug(alias.lower()):
        progress(f"  '{alias}' resolves to {concrete} — pinning it")

    in_price, out_price = next(
        (v for k, v in CLAUDE_PRICES.items() if k in name), (0.0, 0.0))
    label = name[len("claude-cli-"):]
    path = config.MODELS_DIR / f"{name}.yaml"
    if path.exists():
        progress(f"  = {name}  (already registered, untouched)")
        return None
    path.write_text(CLAUDE_TEMPLATE.format(
        alias=label, model_id=concrete, enabled=str(enabled).lower(),
        in_price=in_price, out_price=out_price), encoding="utf-8")
    progress(f"  + {name}  ({concrete})  [pinned]")
    return path
