
from . import config


_KNOWN_SAMPLING = ("top_p", "top_k", "min_p", "top_a", "seed",
                   "repetition_penalty", "presence_penalty", "frequency_penalty")

_RANGES = {
    "temperature": (0.0, 2.0, False),
    "top_p": (0.0, 1.0, False),
    "top_k": (0, 100000, True),
    "min_p": (0.0, 1.0, False),
    "top_a": (0.0, 1.0, False),
    "repetition_penalty": (0.0, 2.0, False),
    "presence_penalty": (-2.0, 2.0, False),
    "frequency_penalty": (-2.0, 2.0, False),
}


def _check_values(where: str, vals: dict, out: list) -> None:
    for k, v in (vals or {}).items():
        if k == "temperature":
            pass
        elif k not in _KNOWN_SAMPLING:
            out.append(f"{where}: unknown sampling key {k!r} — no adapter forwards "
                       f"it, so it would be silently dropped. Known: "
                       f"{', '.join(_KNOWN_SAMPLING)}")
            continue
        lo, hi, is_int = _RANGES.get(k, (None, None, False))
        if lo is None or v is None:
            continue
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            out.append(f"{where}: {k} must be a number, got {v!r}")
        elif is_int and isinstance(v, float) and v != int(v):
            out.append(f"{where}: {k} must be an integer, got {v!r}")
        elif not (lo <= v <= hi):
            out.append(f"{where}: {k}={v} is outside the accepted range {lo}–{hi}")


def validate_models(models=None) -> list[str]:
    from .registry import load_models
    models = models or load_models(include_disabled=True)
    out: list[str] = []
    names: dict[str, str] = {}
    for m in models:
        w = f"{m.source_file or m.name}"
        if not m.sampling_settable:
            why = m.unsettable_reason
            if m.temperature is not None:
                out.append(f"{w}: temperature={m.temperature} but {why} — the value "
                           f"is never sent. Use `temperature: null`.")
            if m.sampling:
                out.append(f"{w}: sampling {sorted(m.sampling)} set but {why} — "
                           f"never sent.")
            if m.sampling_profiles:
                out.append(f"{w}: sampling_profiles set but {why} — never sent.")
        if m.effort is not None:
            if not m.effort_settable:
                out.append(f"{w}: effort={m.effort!r} but only the subscription "
                           f"CLI transports (claude-cli, codex-cli) take an "
                           f"effort level; provider {m.provider} would never "
                           f"receive it. Remove the key.")
            elif str(m.effort) not in m.effort_levels:
                out.append(f"{w}: effort={m.effort!r} is not a level the CLI "
                           f"accepts ({m.provider}). Valid: "
                           f"{', '.join(m.effort_levels)}")
        if m.thinking_off_in_yaml:
            out.append(f"{w}: thinking_off is a probe-only parameter and must "
                       f"not appear in a model yaml — a scored run has to use "
                       f"the model's own default, and only ~8 of the fleet can "
                       f"honour the flag at all. Use the /special thinking probe.")
        if (m.sampling_settable_yaml is False
                and not m.sampling_unsettable_reason.strip()
                and not m.sampling_source.strip()):
            out.append(f"{w}: sampling_settable: false with no "
                       f"sampling_unsettable_reason and no sampling_source — the "
                       f"claim that this model takes no sampling needs a source, "
                       f"since a gateway cannot be asked and will not complain")
        _check_values(w, {"temperature": m.temperature} if m.temperature is not None
                      else {}, out)
        _check_values(w, m.sampling, out)
        for prof, vals in (m.sampling_profiles or {}).items():
            if not isinstance(vals, dict):
                out.append(f"{w}: sampling_profiles.{prof} must be a mapping")
                continue
            _check_values(f"{w} profile {prof!r}", vals, out)
            if prof not in set(config.CATEGORY_SAMPLING_PROFILE.values()):
                out.append(
                    f"{w}: profile {prof!r} is never used — no task category maps "
                    f"to it. Known profiles: "
                    f"{', '.join(sorted(set(config.CATEGORY_SAMPLING_PROFILE.values())))}")
        src = (m.sampling_source or "").strip()
        if src and not src.startswith(("http://", "https://")):
            out.append(f"{w}: sampling_source must be a URL, got {src!r}")
        if (m.sampling or m.sampling_profiles) and not src and m.sampling_settable:
            out.append(f"{w}: sampling is set but sampling_source is empty — record "
                       f"the creator page the values came from, or the numbers have "
                       f"no provenance")
        if not m.max_tokens or m.max_tokens < 1:
            out.append(f"{w}: max_tokens must be a positive integer")
        if m.provider == "openai" and not m.base_url:
            out.append(f"{w}: provider openai needs a base_url")
        if m.key_env and not m.local and m.enabled:
            import os
            if not os.environ.get(m.key_env):
                out.append(f"{w}: key_env {m.key_env} is not set in the environment "
                           f"— every request will fail auth")
        prev = names.get(m.name)
        if prev:
            out.append(f"{w}: duplicate model name {m.name!r} (also in {prev})")
        names[m.name] = w
    return out
