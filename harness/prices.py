"""Refresh gateway list prices into the model yamls.

A model's `pricing:` is captured when it is registered and then never moves —
but providers change prices, and OpenRouter's promotional `:free` variants stop
being free. A frozen snapshot quietly turns into a lie, and the reports say so
on /info. This re-reads the live catalog and writes the current numbers back,
stamping `pricing_asof:` so the snapshot's age is visible instead of implied.

What it does NOT do: rewrite history. `cost_usd` is computed and stored per
result at RUN time, so refreshing prices never changes an already-recorded cost
(and for gateway models that cost was the actual billed amount anyway). New
prices apply to future runs and to anything that displays list price.

    harness prices              # dry run — show what changed
    harness prices --apply      # write the yamls
"""

import re
from datetime import date
from pathlib import Path

from . import config
from .interfaces import list_remote_models, load_interfaces

CATALOG_PROVIDERS = ("openai", "anthropic")


def _catalog_prices() -> dict[str, tuple[float, float]]:
    """model id -> (input_per_mtok, output_per_mtok) across every configured
    interface that publishes pricing."""
    out: dict[str, tuple[float, float]] = {}
    for iface in (load_interfaces() or []):
        try:
            for e in list_remote_models(iface):
                if e.get("in_price") is not None:
                    out[e["id"]] = (e["in_price"], e["out_price"])
        except (RuntimeError, Exception):
            continue
    return out


def _apply_to_yaml(path: Path, in_p: float, out_p: float, asof: str) -> None:
    """Line-edit the pricing (and stamp pricing_asof). Not a yaml round-trip —
    safe_dump would strip the comments these files carry on purpose."""
    text = path.read_text(encoding="utf-8")
    new = f"pricing: {{ input_per_mtok: {in_p}, output_per_mtok: {out_p} }}"
    if re.search(r"^pricing:.*$", text, re.M):
        text = re.sub(r"^pricing:.*$", new, text, count=1, flags=re.M)
    else:
        text = text.rstrip("\n") + "\n" + new + "\n"
    if re.search(r"^pricing_asof:.*$", text, re.M):
        text = re.sub(r"^pricing_asof:.*$", f"pricing_asof: {asof}", text,
                      count=1, flags=re.M)
    else:
        text = text.rstrip("\n") + f"\npricing_asof: {asof}\n"
    path.write_text(text, encoding="utf-8")


def refresh(apply: bool = False, progress=print) -> dict:
    """Compare each registered catalog-priced model against the live catalog."""
    from .registry import load_models

    live = _catalog_prices()
    if not live:
        progress("no catalog pricing reachable — check keys in .env")
        return {"checked": 0, "changed": [], "applied": apply}

    asof = date.today().isoformat()
    changed, unchanged, missing = [], 0, []
    for mo in load_models(include_disabled=True):
        if mo.local or mo.provider not in CATALOG_PROVIDERS:
            continue
        cur = live.get(mo.model)
        if cur is None:
            missing.append(mo.name)
            continue
        old_in = float((mo.pricing or {}).get("input_per_mtok", 0.0))
        old_out = float((mo.pricing or {}).get("output_per_mtok", 0.0))
        new_in, new_out = cur
        if abs(old_in - new_in) < 1e-9 and abs(old_out - new_out) < 1e-9:
            unchanged += 1
            continue
        rec = {"model": mo.name, "id": mo.model,
               "old": (old_in, old_out), "new": (new_in, new_out),
               "was_free": old_in == 0 and old_out == 0 and (new_in or new_out)}
        changed.append(rec)
        if apply:
            p = config.MODELS_DIR / f"{mo.name}.yaml"
            if p.is_file():
                _apply_to_yaml(p, new_in, new_out, asof)

    for c in changed:
        flag = "  ** free tier ENDED **" if c["was_free"] else ""
        progress(f"  {c['model']:34s} {c['old'][0]}/{c['old'][1]}"
                 f"  ->  {c['new'][0]}/{c['new'][1]}{flag}")
    progress(f"{len(changed)} changed, {unchanged} unchanged, "
             f"{len(missing)} not in catalog"
             + (f" (as of {asof}, written)" if apply else " — dry run"))
    return {"checked": len(changed) + unchanged, "changed": changed,
            "missing": missing, "asof": asof, "applied": apply}
