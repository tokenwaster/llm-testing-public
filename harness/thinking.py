import dataclasses

from . import config
from .util import read_json

CANDIDATES = {
    "ext-001-fields-json": "field extraction — mechanical, no derivation",
    "ext-002-nested-normalize": "structure normalisation — mostly mechanical",
    "if-001-format-exact": "format compliance — thinking may actively hurt",
    "if-002-constraint-stack": "constraint tracking, not derivation",
    "tool-001-select-call": "pick a tool and emit JSON",
    "hl-001-grounded-qa": "the answer is in the passage — a lookup",
    "ctx-003-recall-32k": "needle retrieval — latency case, not token case",
    "ctx-004-recall-64k": "needle retrieval — latency case, not token case",
    "ctx-008-recall-128k": "needle retrieval — latency case, not token case",
}

TAG_ON = "thinking:on"
TAG_OFF = "thinking:off"

SUPPORT_PROMPT = ("A train departs at 3:47 PM and travels for 2 hours and "
                  "38 minutes. What time does it arrive? Reply with only the "
                  "time, formatted like 1:05 AM.")


def eligible_models(models=None) -> list:
    from .registry import load_models
    models = models if models is not None else load_models()
    return [m for m in models if m.thinking_toggle_settable]


def probe_matrix(models=None, tasks=None) -> dict:
    from .tasks import load_tasks
    ids = {t.id for t in (tasks if tasks is not None else load_tasks())}
    live = [t for t in CANDIDATES if t in ids]
    return {m.name: list(live) for m in eligible_models(models)}


def _reasoning_tokens(usage: dict, message: dict) -> int:
    det = (usage or {}).get("completion_tokens_details") or {}
    rt = det.get("reasoning_tokens")
    if rt is not None:
        return int(rt)
    text = (message or {}).get("reasoning") or \
           (message or {}).get("reasoning_content") or ""
    return round(len(text) / 4)


def check_support(model, timeout_s: int = 120) -> dict:
    import os

    import httpx
    if not model.thinking_toggle_settable:
        return {"verdict": "unsupported",
                "detail": model.thinking_unsettable_reason}
    key = os.environ.get(model.key_env or "", "")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    url = (model.base_url or "").rstrip("/") + "/chat/completions"

    def call(extra):
        body = {"model": model.model, "max_tokens": 1200,
                "messages": [{"role": "user", "content": SUPPORT_PROMPT}]}
        if model.temperature is not None:
            body["temperature"] = model.temperature
        body.update(extra)
        r = httpx.post(url, headers=headers, json=body, timeout=timeout_s)
        if r.status_code != 200:
            return {"http": r.status_code, "err": r.text[:200]}
        d = r.json()
        ch = (d.get("choices") or [{}])[0]
        return {"http": 200,
                "reas": _reasoning_tokens(d.get("usage") or {},
                                          ch.get("message") or {}),
                "out": (d.get("usage") or {}).get("completion_tokens")}

    try:
        base = call({})
        off = call({"reasoning": {"enabled": False}})
    except httpx.HTTPError as e:
        return {"verdict": "error", "detail": f"{type(e).__name__}: {e}"[:160]}

    if "err" in base:
        return {"verdict": "error",
                "detail": f"baseline HTTP {base['http']}: {base['err'][:120]}"}
    if "err" in off:
        return {"verdict": "refused",
                "detail": f"HTTP {off['http']}: {off['err'][:120]}",
                "base_reasoning": base["reas"]}
    rb, ro = base["reas"], off["reas"]
    if rb < 20:
        return {"verdict": "inconclusive", "base_reasoning": rb,
                "off_reasoning": ro,
                "detail": "the model did not think on the support prompt, so "
                          "compliance cannot be judged from it"}
    if ro <= max(5, 0.10 * rb):
        return {"verdict": "honoured", "base_reasoning": rb, "off_reasoning": ro,
                "detail": f"reasoning {rb} → {ro} tokens"}
    if ro >= 0.5 * rb:
        return {"verdict": "ignored", "base_reasoning": rb, "off_reasoning": ro,
                "detail": f"accepted with no effect: reasoning {rb} → {ro}"}
    return {"verdict": "partial", "base_reasoning": rb, "off_reasoning": ro,
            "detail": f"partially applied: reasoning {rb} → {ro}"}


SUPPORT_PATH = config.SPECIAL_DIR / "thinking-support.json"

REFUSING = ("refused", "unsupported", "error")


def load_support() -> dict:
    return read_json(SUPPORT_PATH, {}) or {}


def save_support(name: str, result: dict) -> dict:
    from .util import write_json
    known = load_support()
    known[name] = result
    SUPPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_json(SUPPORT_PATH, known)
    return known


def probe_models(model, tasks):
    on = dataclasses.replace(model, thinking_off=False)
    off = dataclasses.replace(model, thinking_off=True)
    return [(on, TAG_ON, tasks), (off, TAG_OFF, tasks)]


def _legs() -> dict:
    out = {TAG_ON: [], TAG_OFF: []}
    base = config.SPECIAL_DIR
    if not base.is_dir():
        return out
    for rj in sorted(base.glob("*/run.json")):
        tag = (read_json(rj, {}) or {}).get("tag")
        if tag in out:
            out[tag].append(rj.parent)
    return out


def _cells(run_dirs) -> dict:
    cells: dict = {}
    for rd in run_dirs:
        for mdir in rd.iterdir():
            if not mdir.is_dir():
                continue
            for tdir in mdir.iterdir():
                if not tdir.is_dir():
                    continue
                s = read_json(tdir / "score.json", {}) or {}
                m = read_json(tdir / "metrics.json", {}) or {}
                if s.get("score") is None:
                    continue
                cells.setdefault((mdir.name, tdir.name), []).append(
                    {"score": s["score"],
                     "out": m.get("tokens_out") or 0,
                     "reas": m.get("reasoning_tokens") or 0,
                     "cost": m.get("cost_usd") or 0.0,
                     "wall_ms": m.get("wall_ms") or 0.0})
    return cells


def _mean(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return sum(vals) / len(vals) if vals else None


def results() -> list[dict]:
    legs = _legs()
    on, off = _cells(legs[TAG_ON]), _cells(legs[TAG_OFF])
    rows = []
    for key in sorted(set(on) & set(off)):
        model, task = key
        a, b = on[key], off[key]
        s_on, s_off = _mean(a, "score"), _mean(b, "score")
        o_on, o_off = _mean(a, "out"), _mean(b, "out")
        r_off = _mean(b, "reas") or 0
        r_on = _mean(a, "reas") or 0
        judgeable = r_on >= 20
        complied = judgeable and r_off <= max(5, 0.10 * r_on)
        rows.append({
            "model": model, "task": task, "n_on": len(a), "n_off": len(b),
            "score_on": s_on, "score_off": s_off,
            "score_delta": (None if s_on is None or s_off is None
                            else round(s_off - s_on, 4)),
            "out_on": o_on, "out_off": o_off,
            "out_saved_pct": (None if not o_on or o_off is None
                              else round((1 - o_off / o_on) * 100, 1)),
            "reas_on": r_on, "reas_off": r_off,
            "complied": complied, "judgeable": judgeable,
            "cost_on": _mean(a, "cost"), "cost_off": _mean(b, "cost"),
            "wall_on": _mean(a, "wall_ms"), "wall_off": _mean(b, "wall_ms"),
        })
    return rows


def cost_rollup(rows: list[dict] | None = None, n_floor: int = 3) -> dict:
    rows = results() if rows is None else rows
    per: dict[str, dict] = {}
    for r in rows:
        v = verdict(r, n_floor)
        a = per.setdefault(r["model"], {
            "model": r["model"], "cells": 0, "applied": 0, "free": 0,
            "required": 0, "cost_on": 0.0, "cost_off": 0.0,
            "out_on": 0.0, "out_off": 0.0, "wall_on": 0.0, "wall_off": 0.0,
            "free_cost_on": 0.0, "free_cost_off": 0.0,
            "free_wall_on": 0.0, "free_wall_off": 0.0, "probe_cost": 0.0})
        a["cells"] += 1
        a["probe_cost"] += (r.get("cost_on") or 0) * (r.get("n_on") or 0) \
            + (r.get("cost_off") or 0) * (r.get("n_off") or 0)
        if not r.get("complied"):
            continue
        a["applied"] += 1
        for k in ("cost", "out", "wall"):
            a[f"{k}_on"] += r.get(f"{k}_on") or 0
            a[f"{k}_off"] += r.get(f"{k}_off") or 0
        if v == "free saving":
            a["free"] += 1
            a["free_cost_on"] += r.get("cost_on") or 0
            a["free_cost_off"] += r.get("cost_off") or 0
            a["free_wall_on"] += r.get("wall_on") or 0
            a["free_wall_off"] += r.get("wall_off") or 0
        elif v == "thinking required":
            a["required"] += 1

    def pct(on, off):
        return None if not on else round((1 - off / on) * 100, 1)

    out = []
    for a in per.values():
        a["cost_saved"] = round(a["cost_on"] - a["cost_off"], 6)
        a["cost_saved_pct"] = pct(a["cost_on"], a["cost_off"])
        a["out_saved_pct"] = pct(a["out_on"], a["out_off"])
        a["wall_saved_pct"] = pct(a["wall_on"], a["wall_off"])
        a["free_cost_saved"] = round(a["free_cost_on"] - a["free_cost_off"], 6)
        a["free_cost_saved_pct"] = pct(a["free_cost_on"], a["free_cost_off"])
        a["free_wall_saved_pct"] = pct(a["free_wall_on"], a["free_wall_off"])
        a["probe_cost"] = round(a["probe_cost"], 6)
        out.append(a)
    out.sort(key=lambda a: -(a["free_cost_saved"] or 0))
    total = {
        "cells": sum(a["cells"] for a in out),
        "applied": sum(a["applied"] for a in out),
        "free": sum(a["free"] for a in out),
        "required": sum(a["required"] for a in out),
        "free_cost_saved": round(sum(a["free_cost_saved"] for a in out), 6),
        "free_cost_on": round(sum(a["free_cost_on"] for a in out), 6),
        "probe_cost": round(sum(a["probe_cost"] for a in out), 6),
    }
    total["free_cost_saved_pct"] = pct(total["free_cost_on"],
                                       total["free_cost_on"]
                                       - total["free_cost_saved"])
    total["payback_runs"] = (
        None if not total["free_cost_saved"]
        else round(total["probe_cost"] / total["free_cost_saved"], 1))
    return {"models": out, "total": total, "n_floor": n_floor}


def verdict(row: dict, n_floor: int = 3) -> str:
    if not row.get("complied"):
        if "judgeable" in row and not row["judgeable"]:
            return "nothing to disable"
        return "not applied"
    if min(row.get("n_on") or 0, row.get("n_off") or 0) < n_floor:
        return "needs repeats"
    d = row.get("score_delta")
    if d is None:
        return "no score"
    if d <= -0.05:
        return "thinking required"
    if (row.get("out_saved_pct") or 0) >= 10:
        return "free saving"
    return "no material change"
