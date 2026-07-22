"""LM Studio lifecycle control: model states via the /api/v0 REST API, and
explicit load / unload via the `lms` CLI.

Used by the runner so local timing is honest and deterministic:
  1. `lms unload --all`  — clear VRAM/RAM of every other model
  2. `lms load <key>`    — explicit pre-load, measured as preload_ms
  3. warm-up ping        — verifies serving; its latency is the *warm* baseline
"""

import os
import shutil
from pathlib import Path

import httpx

from .util import now_ms, run_capped

LOAD_TIMEOUT_S = 900
UNLOAD_TIMEOUT_S = 120


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
    """{model_id: 'loaded' | 'not-loaded'} for every model DOWNLOADED in LM
    Studio (llm/vlm only), or None if the v0 API is unreachable."""
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
    """Identity of the model FILE (quantization, arch, max context) from the
    v0 API — the model-side analogue of task content-hashing."""
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
    """Explicitly load a model; returns wall-clock load time in ms, or None
    if lms is unavailable or the load failed (caller falls back to JIT).

    gpu_offload: "max" (force every layer onto the GPU — fast, for contexts that
    fit), "off", or a "0".."1" ratio — passed as `--gpu <value>`. "auto" (or "")
    means OMIT the flag, i.e. lms's own default auto-fit — lms rejects a literal
    `--gpu auto` ("not a number"). Use "auto" for contexts that overflow VRAM, so
    lms parks the excess on the CPU and the task COMPLETES instead of "max"
    forcing a shared-memory spill; use "max" (with batch-sized context via
    context_buckets) so the whole model sits on the GPU when it fits."""
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
