import dataclasses

from . import config
from .util import read_json

TAG_PREFIX = "avenue:"

AVENUES = {
    "cli": "subscription via the claude CLI",
    "api": "direct pay-per-token API",
    "gateway": "gateway (OpenRouter)",
}

PROVIDER_AVENUE = {
    "claude-cli": "cli",
    "anthropic": "api",
}

BILLED_AVENUES = ("gateway",)


def avenue_of(model) -> str:
    a = PROVIDER_AVENUE.get(model.provider)
    if a:
        return a
    if "openrouter" in (model.base_url or ""):
        return "gateway"
    return ""


def tag_for(avenue: str) -> str:
    return f"{TAG_PREFIX}{avenue}"


def avenue_from_tag(tag: str) -> str:
    tag = tag or ""
    return tag[len(TAG_PREFIX):] if tag.startswith(TAG_PREFIX) else ""


def _key(model) -> str:
    return (model.compare_key or "").strip()


_CACHE: dict = {}


def reset_caches() -> None:
    global _OH_CACHE
    _OH_CACHE = None
    _CACHE.clear()


def _scope() -> str:
    return f"{config.SPECIAL_DIR}|{config.RUNS_DIR}"


def _cache_get(key):
    return _CACHE.get((_scope(), key))


def _cache_put(key, value):
    _CACHE[(_scope(), key)] = value
    return value


def _all_models():
    if "models" not in _CACHE:
        from .registry import load_models
        _CACHE["models"] = load_models(include_disabled=True)
    return _CACHE["models"]


def groups(models=None) -> dict[str, dict[str, object]]:
    if models is None and _cache_get("groups") is not None:
        return _cache_get("groups")
    models = models if models is not None else _all_models()
    out: dict[str, dict[str, object]] = {}
    for m in models:
        k, a = _key(m), avenue_of(m)
        if not k or not a:
            continue
        out.setdefault(k, {})[a] = m
    out = {k: v for k, v in out.items() if len(v) > 1}
    if models is _CACHE.get("models"):
        _cache_put("groups", out)
    return out


def runnable(models=None) -> dict[str, dict[str, object]]:
    out = {}
    for k, per in groups(models).items():
        live = {a: m for a, m in per.items() if _usable(m)}
        if len(live) > 1:
            out[k] = live
    return out


def _usable(model) -> bool:
    if model.provider == "claude-cli":
        return True
    return bool(model.api_key)


def blocked_reason(model) -> str:
    if _usable(model):
        return ""
    return f"no API key — set {model.key_env} in .env"


def probe_matrix(models=None, tasks=None) -> dict:
    from .tasks import load_tasks
    ids = [t.id for t in (tasks if tasks is not None else load_tasks())]
    return {k: list(ids) for k in runnable(models)}


def probe_models(model, tasks, avenues=None):
    per = runnable().get(_key(model)) or {}
    want = set(avenues) if avenues else None
    legs = []
    for avenue in ("cli", "api", "gateway"):
        mo = per.get(avenue)
        if mo is None or (want is not None and avenue not in want):
            continue
        legs.append((dataclasses.replace(mo, enabled=True), tag_for(avenue), tasks))
    return legs


def leg_counts(models=None) -> dict:
    name_to_key = {}
    for k, per in groups(models).items():
        for m in per.values():
            name_to_key[m.name] = k
    out: dict = {}
    for avenue, dirs in _legs().items():
        for (mname, tid), entries in _cells(dirs).items():
            k = name_to_key.get(mname)
            if k:
                out[(k, tid, avenue)] = out.get((k, tid, avenue), 0) + len(entries)
    return out


def leg_missing(key, task_ids, target, avenues, counts=None) -> dict:
    counts = leg_counts() if counts is None else counts
    live = set(runnable().get(key) or {})
    want = sorted((set(avenues) & live) if avenues else live)
    out = {}
    for tid in task_ids:
        out[tid] = {a: max(0, int(target) - counts.get((key, tid, a), 0))
                    for a in want}
    return out


def _legs() -> dict[str, list]:
    out: dict[str, list] = {}
    base = config.SPECIAL_DIR
    if not base.is_dir():
        return out
    for rj in sorted(base.glob("*/run.json")):
        avenue = avenue_from_tag((read_json(rj, {}) or {}).get("tag"))
        if avenue in AVENUES:
            out.setdefault(avenue, []).append(rj.parent)
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
                cells.setdefault((mdir.name, tdir.name), []).append({
                    "score": s["score"],
                    "in": m.get("tokens_in") or 0,
                    "out": m.get("tokens_out") or 0,
                    "cache_read": m.get("cache_read_tokens") or 0,
                    "cache_write": m.get("cache_write_tokens") or 0,
                    "cost": m.get("cost_usd"),
                    "cost_source": m.get("cost_source"),
                    "wall_ms": m.get("wall_ms") or 0.0,
                })
    return cells


def _mean(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return sum(vals) / len(vals) if vals else None


def results(models=None) -> list[dict]:
    if models is None and _cache_get("results") is not None:
        return _cache_get("results")
    _want = models is None
    by_avenue = {a: _cells(dirs) for a, dirs in _legs().items()}
    name_to_key, key_to_avenue = {}, {}
    for k, per in groups(models).items():
        for a, m in per.items():
            name_to_key[m.name] = k
            key_to_avenue[(k, a)] = m.name

    rows: dict[tuple, dict] = {}
    for avenue, cells in by_avenue.items():
        for (mname, tid), entries in cells.items():
            k = name_to_key.get(mname)
            if not k:
                continue
            slot = rows.setdefault((k, tid), {"compare_key": k, "task": tid,
                                              "avenues": {}})
            slot["avenues"][avenue] = {
                "model": mname, "n": len(entries),
                "score": _mean(entries, "score"),
                "in": _mean(entries, "in"), "out": _mean(entries, "out"),
                "cache_read": _mean(entries, "cache_read"),
                "cache_write": _mean(entries, "cache_write"),
                "cost": _mean(entries, "cost"),
                "wall_ms": _mean(entries, "wall_ms"),
                "billed": any(e.get("cost_source") == "billed" for e in entries),
            }
    live = runnable(models)
    out = []
    for row in rows.values():
        if len(row["avenues"]) < 2:
            continue
        row["paired"] = sorted(row["avenues"])
        expected = set(live.get(row["compare_key"]) or row["avenues"])
        row["expected"] = sorted(expected)
        row["missing"] = sorted(expected - set(row["avenues"]))
        row["trials"] = (0 if row["missing"]
                         else min(v["n"] for v in row["avenues"].values()))
        base = row["avenues"].get("api") or row["avenues"][row["paired"][0]]
        for a, v in row["avenues"].items():
            v["in_vs_api"] = (None if not base["in"] or v["in"] is None
                              else round(v["in"] / base["in"], 3))
            v["cost_vs_api"] = (None if not base["cost"] or v["cost"] is None
                                else round(v["cost"] / base["cost"], 3))
            v["score_vs_api"] = (None if base["score"] is None or v["score"] is None
                                 else round(v["score"] - base["score"], 4))
        out.append(row)
    out.sort(key=lambda r: (r["compare_key"], r["task"]))
    if _want:
        _cache_put("results", out)
    return out


def rollup(rows: list[dict] | None = None) -> dict:
    rows = results() if rows is None else rows
    per: dict[str, dict] = {}
    for r in rows:
        a = per.setdefault(r["compare_key"], {
            "compare_key": r["compare_key"], "tasks": 0,
            "avenues": {}, "billed_avenues": set()})
        a["tasks"] += 1
        for name, v in r["avenues"].items():
            slot = a["avenues"].setdefault(name, {
                "avenue": name, "model": v["model"], "cells": 0,
                "cost": 0.0, "in": 0.0, "out": 0.0, "wall_ms": 0.0,
                "score_sum": 0.0, "scored": 0})
            slot["cells"] += 1
            slot["cost"] += v["cost"] or 0.0
            slot["in"] += v["in"] or 0.0
            slot["out"] += v["out"] or 0.0
            slot["wall_ms"] += v["wall_ms"] or 0.0
            if v["score"] is not None:
                slot["score_sum"] += v["score"]
                slot["scored"] += 1
            if v["billed"]:
                a["billed_avenues"].add(name)
    out = []
    for a in per.values():
        for slot in a["avenues"].values():
            slot["score"] = (round(slot["score_sum"] / slot["scored"], 4)
                             if slot["scored"] else None)
        a["billed_avenues"] = sorted(a["billed_avenues"])
        api = a["avenues"].get("api")
        for name, slot in a["avenues"].items():
            slot["cost_vs_api"] = (None if not (api and api["cost"])
                                   else round(slot["cost"] / api["cost"], 3))
            slot["in_vs_api"] = (None if not (api and api["in"])
                                 else round(slot["in"] / api["in"], 3))
        a["avenues"] = [a["avenues"][k] for k in sorted(a["avenues"])]
        out.append(a)
    out.sort(key=lambda a: a["compare_key"])
    return {"models": out, "n_pairs": sum(a["tasks"] for a in out),
            "avenue_labels": AVENUES}


_OH_CACHE: dict | None = None


def overhead_per_request(rows: list[dict] | None = None) -> dict:
    global _OH_CACHE
    want_cache = rows is None
    if want_cache and _OH_CACHE is not None:
        return _OH_CACHE
    rows = results() if rows is None else rows
    per: dict[str, list] = {}
    for r in rows:
        c, a = r["avenues"].get("cli"), r["avenues"].get("api")
        if not (c and a and c.get("in") and a.get("in")):
            continue
        per.setdefault(r["compare_key"], []).append(c["in"] - a["in"])
    out = {k: {"tokens": sum(v) / len(v), "n": len(v),
               "spread": max(v) - min(v)} for k, v in per.items() if v}
    if want_cache:
        _OH_CACHE = out
    return out


def cli_overhead_for(model) -> float | None:
    oh = overhead_per_request().get(model.compare_key or "")
    return oh["tokens"] if oh else None


def requests_in(metrics: dict) -> int:
    return (max(1, metrics.get("turns") or 1)
            * max(1, metrics.get("n_attempts") or 1))


def api_equivalent(metrics: dict, model) -> dict | None:
    if avenue_of(model) != "cli":
        return None
    oh = cli_overhead_for(model)
    if oh is None:
        return None
    pr = model.pricing or {}
    if pr.get("input_per_mtok") is None or pr.get("output_per_mtok") is None:
        return None
    rate_in = float(pr["input_per_mtok"])
    rate_out = float(pr["output_per_mtok"])
    tin = metrics.get("tokens_in") or 0
    tout = metrics.get("tokens_out") or 0
    n = requests_in(metrics)
    scaffold = min(tin, oh * n)
    content = max(0, tin - scaffold)
    return {"content_tokens": content, "scaffold_tokens": scaffold,
            "requests": n,
            "cost": content / 1e6 * rate_in + tout / 1e6 * rate_out}


def accuracy(rows: list[dict] | None = None) -> dict:
    if rows is None and _cache_get("accuracy") is not None:
        return _cache_get("accuracy")
    want_cache = rows is None
    rows = results() if rows is None else rows
    oh = overhead_per_request(rows)
    in_err, out_ratio, n = [], {}, 0
    for r in rows:
        c, a = r["avenues"].get("cli"), r["avenues"].get("api")
        if not (c and a and a.get("in")):
            continue
        k = r["compare_key"]
        if k not in oh:
            continue
        n += 1
        pred = max(0, (c["in"] or 0) - oh[k]["tokens"])
        in_err.append(abs(pred - a["in"]) / a["in"] * 100)
        if c.get("out") and a.get("out"):
            out_ratio.setdefault(k, []).append(c["out"] / a["out"])
    ratios = {k: sum(v) / len(v) for k, v in out_ratio.items() if v}
    out = {
        "n": n,
        "input_mean_err_pct": (round(sum(in_err) / len(in_err), 1)
                               if in_err else None),
        "input_worst_err_pct": round(max(in_err), 1) if in_err else None,
        "out_ratio": {k: round(v, 2) for k, v in sorted(ratios.items())},
        "out_ratio_lo": round(min(ratios.values()), 2) if ratios else None,
        "out_ratio_hi": round(max(ratios.values()), 2) if ratios else None,
        "models": sorted(oh),
        "overhead": {k: int(v["tokens"]) for k, v in sorted(oh.items())},
    }
    if want_cache:
        _cache_put("accuracy", out)
    return out


def overhead_summary() -> dict:
    if _cache_get("ohs") is not None:
        return _cache_get("ohs")
    from . import config
    from .registry import load_models
    from .util import read_json
    mods = {m.name: m for m in load_models(include_disabled=True)}
    per: dict[str, dict] = {}
    if not config.RUNS_DIR.is_dir():
        return {"models": [], "total": {}}
    for mf in config.RUNS_DIR.glob("*/*/*/metrics.json"):
        name = mf.parents[1].name
        mo = mods.get(name)
        if mo is None or avenue_of(mo) != "cli":
            continue
        d = read_json(mf, {}) or {}
        est = api_equivalent(d, mo)
        if est is None:
            continue
        a = per.setdefault(name, {"model": name, "cells": 0, "tokens_in": 0,
                                  "scaffold": 0, "cost": 0.0, "equiv": 0.0})
        a["cells"] += 1
        a["tokens_in"] += d.get("tokens_in") or 0
        a["scaffold"] += int(est["scaffold_tokens"])
        a["cost"] += d.get("cost_usd") or 0
        a["equiv"] += est["cost"]
    out = sorted(per.values(), key=lambda a: a["model"])
    for a in out:
        a["scaffold_pct"] = (round(100 * a["scaffold"] / a["tokens_in"], 1)
                             if a["tokens_in"] else None)
        a["saved"] = round(a["cost"] - a["equiv"], 4)
    tin = sum(a["tokens_in"] for a in out)
    res = {"models": out, "total": {
        "cells": sum(a["cells"] for a in out),
        "tokens_in": tin,
        "scaffold": sum(a["scaffold"] for a in out),
        "scaffold_pct": (round(100 * sum(a["scaffold"] for a in out) / tin, 1)
                         if tin else None),
        "cost": round(sum(a["cost"] for a in out), 4),
        "equiv": round(sum(a["equiv"] for a in out), 4),
    }}
    _cache_put("ohs", res)
    return res


def verdict(row: dict) -> str:
    av = row.get("avenues") or {}
    if len(av) < 2:
        return "unpaired"
    if row.get("missing"):
        return "missing " + ", ".join(row["missing"])
    scores = [v["score"] for v in av.values() if v["score"] is not None]
    if len(scores) < 2:
        return "no score"
    if max(scores) - min(scores) >= 0.05:
        return "avenue changed the score"
    costs = [v["cost"] for v in av.values() if v["cost"]]
    if len(costs) >= 2 and max(costs) / min(costs) >= 1.10:
        return "same score, different price"
    ins = [v["in"] for v in av.values() if v["in"]]
    if len(ins) >= 2 and max(ins) / min(ins) >= 1.10:
        return "same price, different tokens"
    return "no material difference"
