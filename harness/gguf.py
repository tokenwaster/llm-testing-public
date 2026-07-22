"""GGUF header analysis for local models: weights size, KV-cache cost,
sliding-window awareness, native context — powering the /run page's
fit-advisor (context warnings + spill warnings + quant suggestions).

Everything here is DISK-ONLY: no LM Studio traffic, safe during runs.
Estimates assume fp16 KV cache and ~30GB usable of the 32GB card.
"""

import struct
from pathlib import Path

BUDGET_BYTES = int(30.0 * 1e9)
FALLBACK_FULL_CTX = 120_000
SLOW_TPS_NOTE = "expect single-digit tok/s"


def task_windows_from(tasks, max_tokens: int = 32768) \
        -> list[tuple[str, int, int]]:
    """(task_id, load_window, min_window) per long-context task, from the LIVE
    task set. load_window (prompt/3 + gen budget) drives spill predictions;
    min_window (prompt + answer margin) drives feasibility — a 2k-prompt task
    fits a 32k window even if the full gen budget doesn't."""
    out = []
    for t in tasks:
        if getattr(t, "category", "") == "long-context":
            plen = len(t.prompt) // 3
            out.append((t.id, plen + max_tokens + 1024, plen + 2048))
    return sorted(out, key=lambda x: -x[1])

_MODELS_DIR = Path.home() / ".lmstudio" / "models"
_T_FMT = {0: ("B", 1), 1: ("b", 1), 2: ("H", 2), 3: ("h", 2), 4: ("I", 4),
          5: ("i", 4), 6: ("f", 4), 7: ("?", 1), 10: ("Q", 8), 11: ("q", 8),
          12: ("d", 8)}

_meta_cache: dict[tuple, dict] = {}
_file_index: dict[str, Path] | None = None


def _norm(s: str) -> str:
    return "".join(c for c in s if c.isalnum()).lower()


def find_gguf(model_id: str) -> Path | None:
    """Locate the downloaded GGUF for an LM Studio model id."""
    global _file_index
    if _file_index is None or model_id not in _file_index:
        _file_index = {}
        if _MODELS_DIR.exists():
            for p in _MODELS_DIR.rglob("*.gguf"):
                if "mmproj" not in p.name.lower():
                    _file_index[_norm(p.name)] = p
    tail = _norm(model_id.split("/")[-1])
    for name, p in _file_index.items():
        if tail in name or name.startswith(tail[:12]):
            return p
    return None


def read_meta(path: Path) -> dict:
    """Parse GGUF metadata (header only). Early-exits at tokenizer keys —
    model params always precede them. Cached by (path, size, mtime)."""
    st = path.stat()
    key = (str(path), st.st_size, st.st_mtime_ns)
    if key in _meta_cache:
        return _meta_cache[key]
    out: dict = {}
    try:
        with open(path, "rb") as f:
            if f.read(4) != b"GGUF":
                return out
            _ver, _nt, n_kv = struct.unpack("<IQQ", f.read(20))

            def rstr():
                (n,) = struct.unpack("<Q", f.read(8))
                return f.read(n).decode("utf-8", "replace")

            def rval(t):
                if t in _T_FMT:
                    fmt, size = _T_FMT[t]
                    return struct.unpack("<" + fmt, f.read(size))[0]
                if t == 8:
                    return rstr()
                if t == 9:
                    et, cnt = struct.unpack("<IQ", f.read(12))
                    if et in _T_FMT:
                        if cnt > 128:
                            f.seek(_T_FMT[et][1] * cnt, 1)
                            return None
                        return [rval(et) for _ in range(cnt)]
                    return [rval(et) for _ in range(cnt)]
                raise ValueError(f"gguf type {t}")

            for _ in range(n_kv):
                k = rstr()
                if k.startswith("tokenizer."):
                    break
                (t,) = struct.unpack("<I", f.read(4))
                out[k] = rval(t)
    except (OSError, struct.error, ValueError):
        return {}
    _meta_cache[key] = out
    return out


def _kv_components(path: "Path", meta: dict) -> dict | None:
    """(weights, kv_per_tok, kv_fixed bytes) + native_ctx/sliding/quant for a
    GGUF, from its header. Shared by advise() and footprint(). None when the
    header lacks the attention dims we need."""
    arch = meta.get("general.architecture")
    if not arch:
        return None
    p = lambda k, d=None: meta.get(f"{arch}.{k}", d)
    layers, kvh = p("block_count"), p("attention.head_count_kv")
    heads = p("attention.head_count")
    if isinstance(heads, list):
        heads = max(heads)
    kdim = p("attention.key_length") or (
        (p("embedding_length") // heads) if heads else None)
    vdim = p("attention.value_length") or kdim
    native = p("context_length") or 0
    sliding = p("attention.sliding_window") or 0
    if not (layers and kvh and kdim):
        return None

    weights = path.stat().st_size
    if isinstance(kvh, list):
        if sliding:
            lo = min(kvh)
            glob = [v for v in kvh if v == lo] or kvh
            per_tok = sum(glob) * (kdim + vdim) * 2
            fixed = (sum(kvh) - sum(glob)) * (kdim + vdim) * 2 * sliding
        else:
            per_tok = sum(kvh) * (kdim + vdim) * 2
            fixed = 0
    elif sliding:
        per_tok = (layers / 4) * kvh * (kdim + vdim) * 2
        fixed = (layers * 3 / 4) * kvh * (kdim + vdim) * 2 * sliding
    else:
        per_tok = layers * kvh * (kdim + vdim) * 2
        fixed = 0
    quant = path.stem.rsplit("-", 1)[-1] if "-" in path.stem else "?"
    return {"weights": weights, "per_tok": per_tok, "fixed": fixed,
            "native": native, "sliding": sliding, "quant": quant}


def footprint(model_id: str) -> dict | None:
    """Raw VRAM components so a fit gate works at ANY GPU size and context:

        needed_gb(ctx) = weights_gb + kv_fixed_gb + kv_per_tok_gb * ctx

    None when the GGUF is absent or its header lacks the attention dims. The
    honest 'will it fit MY card' basis — unlike measured peak VRAM, which is
    entangled with whatever context the run happened to load."""
    path = find_gguf(model_id)
    if not path:
        return None
    comp = _kv_components(path, read_meta(path))
    if not comp:
        return None
    return {"weights_gb": round(comp["weights"] / 1e9, 2),
            "kv_per_tok_gb": comp["per_tok"] / 1e9,
            "kv_fixed_gb": comp["fixed"] / 1e9,
            "native_ctx": comp["native"], "quant": comp["quant"]}


def advise(model_id: str, yaml_cap: int = 0, max_tokens: int = 32768,
           evidence: dict | None = None,
           task_windows: list[tuple[str, int]] | None = None) -> dict | None:
    """Fit analysis for one local model; None when the GGUF can't be
    found/parsed. `evidence` (measured reality from past runs) TRUMPS the
    header math — a model that demonstrably ran the full window fast never
    gets a spill warning (attention tricks the naive KV formula can't see,
    e.g. hybrid/linear layers, would otherwise be falsely flagged)."""
    path = find_gguf(model_id)
    if not path:
        return None
    comp = _kv_components(path, read_meta(path))
    if not comp:
        return None
    weights, per_tok, fixed = comp["weights"], comp["per_tok"], comp["fixed"]
    native, sliding, quant = comp["native"], comp["sliding"], comp["quant"]

    free = BUDGET_BYTES - weights - fixed
    max_ctx = int(free / per_tok) if free > 0 and per_tok else 0

    warnings: list[str] = []
    suggestion = None
    ev = evidence or {}
    proven_window = ev.get("proven_window") or 0
    passed = set(ev.get("passed") or ())
    eff = min(x for x in (max_ctx, native or 10**9,
                          yaml_cap or 10**9) if x)

    tw = task_windows or [("(largest ctx task)", FALLBACK_FULL_CTX,
                           FALLBACK_FULL_CTX)]
    full_need = max(w for _, w, _ in tw)

    def infeasible_at(window: int) -> list[str]:
        """Tasks whose PROMPT can't fit the window (with answer margin)."""
        return [tid for tid, _, mn in tw if window < mn]

    fails = [t for t in infeasible_at(eff) if t not in passed]
    tier = "full suite" if not fails else \
        (f"fails {len(fails)}/{len(tw)} ctx tasks")

    load_ctx = min(full_need, yaml_cap or full_need)
    proven_fast = proven_window >= load_ctx

    if weights > BUDGET_BYTES:
        if not proven_fast:
            warnings.append(
                f"weights alone ({weights / 1e9:.0f}GB) exceed VRAM — runs "
                f"only via CPU/MoE offload")
    else:
        if load_ctx > max_ctx and not proven_fast:
            warnings.append(
                f"a {load_ctx // 1000}k window may spill to CPU — "
                f"{SLOW_TPS_NOTE}; set context_length ≤ {max_ctx:,} "
                f"(estimate — a fast run at this window clears it)")
        if native and infeasible_at(native) and \
                (not yaml_cap or yaml_cap > native):
            warnings.append(
                f"native context is only {native:,} — long-context tasks "
                f"beyond it fail regardless of VRAM")
        if fails:
            warnings.append("likely task failures at this window: "
                            + ", ".join(sorted(fails)))
        if native and native < max_tokens + 2048:
            warnings.append(
                f"native window {native:,} barely exceeds the {max_tokens:,} "
                f"generation budget — heavy thinks will die")
        shrink = {"Q8_0": ("Q4_K_M", 0.55), "Q6_K": ("Q4_K_M", 0.72),
                  "Q5_K_M": ("Q4_K_M", 0.85), "Q5_K_L": ("Q4_K_M", 0.83),
                  "Q4_K_M": ("IQ3_XS", 0.75), "Q4_K_S": ("IQ3_XS", 0.78)}
        if warnings and quant in shrink and not sliding:
            new_q, f = shrink[quant]
            new_max = int((BUDGET_BYTES - weights * f - fixed) / per_tok)
            new_fails = [t for t in
                         infeasible_at(min(new_max, native or 10**9))
                         if t not in passed]
            if len(new_fails) < len(fails):
                gain = ("full suite" if not new_fails
                        else f"fails only {len(new_fails)}/{len(tw)} ctx")
                suggestion = (f"redownload at {new_q} "
                              f"(~{weights * f / 1e9:.0f}GB) → "
                              f"~{new_max // 1000}k context ({gain})")

    return {"quant": quant, "weights_gb": round(weights / 1e9, 1),
            "sliding": bool(sliding), "native_ctx": native,
            "max_ctx": max_ctx, "tier": tier,
            "warnings": warnings, "suggestion": suggestion}
