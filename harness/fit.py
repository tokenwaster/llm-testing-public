"""Task-fit classification — which model for which job.

Driven by directives.yaml (thresholds + value-pick rules) so the
classification adapts after every run without code changes."""

import yaml

from . import config

DIRECTIVES_FILE = config.ROOT / "directives.yaml"

DEFAULTS = {
    "thresholds": {"excellent": 0.95, "capable": 0.85, "weak": 0.70},
    "value_pick": {"min_score": 0.85, "min_tps": 120},
    "power": {"cost_per_kwh": 0.15, "currency": "$"},
    "scout": {"promote": 0.6, "borderline": 0.35},
    "note": "",
}


def load_directives() -> dict:
    try:
        data = yaml.safe_load(DIRECTIVES_FILE.read_text(encoding="utf-8")) or {}
    except OSError:
        data = {}
    out = {k: dict(v) if isinstance(v, dict) else v
           for k, v in DEFAULTS.items()}
    for k, v in data.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    return out


def _classify(score: float, th: dict) -> str:
    if score >= th["excellent"]:
        return "excellent"
    if score >= th["capable"]:
        return "capable"
    if score >= th["weak"]:
        return "weak"
    return "avoid"


def task_fit(by_model: dict[str, list[dict]], categories: list[str]) -> dict:
    """by_model: model -> latest-result entries (each with category, score
    dict, gen_tokens_per_sec). Returns {directives, rows: [{category,
    top: [(model, score)], value: [(model, score, tps)], classes:
    {model: (class, score)}}]}."""
    d = load_directives()
    th, vp = d["thresholds"], d["value_pick"]
    rows = []
    for cat in categories:
        stats = {}
        for m, entries in by_model.items():
            es = [e for e in entries if e["category"] == cat
                  and e["score"].get("status") == "scored"]
            if not es:
                continue
            score = sum(e["score"]["score"] for e in es) / len(es)
            tpss = [e.get("gen_tokens_per_sec") for e in es
                    if e.get("gen_tokens_per_sec")]
            stats[m] = {"score": score,
                        "tps": sum(tpss) / len(tpss) if tpss else None}
        if not stats:
            continue
        best = max(s["score"] for s in stats.values())
        top = sorted([(m, s["score"]) for m, s in stats.items()
                      if s["score"] == best])
        value = sorted(
            [(m, s["score"], s["tps"]) for m, s in stats.items()
             if s["score"] >= vp["min_score"] and s["tps"]
             and s["tps"] >= vp["min_tps"]],
            key=lambda x: -(x[2] or 0))
        rows.append({
            "category": cat,
            "top": top,
            "value": value[:2],
            "classes": {m: (_classify(s["score"], th), s["score"])
                        for m, s in sorted(stats.items())},
        })
    return {"directives": d, "rows": rows}


def timeout_risks(tasks, threshold: float = 0.75) -> dict[str, list[str]]:
    """Which model·task pairs are near or past their enforced time budget.
    Since v0.5.10 the total-duration deadline binds every model (not just
    claude-cli), so slowness is now a way to score zero. Grounded in the model's
    OWN slowest observed attempt — not a tok/s extrapolation, which over-predicts
    badly (it put gemma-4-31b at 1850s on web-003, which ran well inside budget)."""
    from . import report

    by_id = {t.id: t for t in tasks}
    slowest: dict[tuple[str, str], float] = {}
    for run in report.load_all_runs():
        for res in run["results"]:
            tid, mod = res.get("task"), res.get("model")
            if tid not in by_id or not mod:
                continue
            for a in res.get("attempts", []):
                dur = (a.get("total_ms") or 0) / 1000
                if dur:
                    key = (mod, tid)
                    slowest[key] = max(slowest.get(key, 0.0), dur)

    out: dict[str, list[str]] = {}
    for (mod, tid), dur in sorted(slowest.items()):
        limit = by_id[tid].timeout_s
        if dur > limit:
            out.setdefault(mod, []).append(
                f"{tid}: slowest run {dur:.0f}s EXCEEDS its {limit}s budget — "
                "will time out")
        elif dur > threshold * limit:
            out.setdefault(mod, []).append(
                f"{tid}: slowest run {dur:.0f}s is {dur / limit:.0%} of its "
                f"{limit}s budget — may time out")
    return out


def set_power_rate(cost_per_kwh: float, currency: str = "$") -> dict:
    """Write the electricity rate into directives.yaml. Line edits, NOT a yaml
    round-trip — safe_dump would strip the file's comments, and directives.yaml
    is heavily commented on purpose."""
    import re

    rate = float(cost_per_kwh)
    if rate < 0:
        raise ValueError("cost_per_kwh must be >= 0")
    cur = (currency or "$")[:3]

    try:
        text = DIRECTIVES_FILE.read_text(encoding="utf-8")
    except OSError:
        text = ""

    if re.search(r"^power:", text, re.M):
        text = re.sub(r"^(\s*cost_per_kwh:\s*)[\d.]+", rf"\g<1>{rate}",
                      text, count=1, flags=re.M)
        text = re.sub(r'^(\s*currency:\s*)".*?"', rf'\g<1>"{cur}"',
                      text, count=1, flags=re.M)
    else:
        text += (f'\npower:\n  cost_per_kwh: {rate}\n  currency: "{cur}"\n')

    DIRECTIVES_FILE.write_text(text, encoding="utf-8", newline="")
    return load_directives().get("power", {})
