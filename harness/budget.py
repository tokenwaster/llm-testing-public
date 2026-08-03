import os

from . import config

BALANCE_TIMEOUT_S = 15


def _openrouter_balance(key: str) -> dict | None:
    import httpx
    h = {"Authorization": f"Bearer {key}"}
    out: dict = {"provider": "openrouter"}
    try:
        r = httpx.get("https://openrouter.ai/api/v1/credits", headers=h,
                      timeout=BALANCE_TIMEOUT_S)
        if r.status_code != 200:
            return {"provider": "openrouter", "error":
                    f"HTTP {r.status_code}: {r.text[:120]}"}
        d = (r.json() or {}).get("data") or {}
        granted = float(d.get("total_credits") or 0)
        used = float(d.get("total_usage") or 0)
        out["remaining"] = round(granted - used, 4)
        out["detail"] = f"${granted:,.2f} granted, ${used:,.2f} used"
    except httpx.HTTPError as e:
        return {"provider": "openrouter", "error": f"{type(e).__name__}: {e}"}
    try:
        r = httpx.get("https://openrouter.ai/api/v1/auth/key", headers=h,
                      timeout=BALANCE_TIMEOUT_S)
        if r.status_code == 200:
            d = (r.json() or {}).get("data") or {}
            lim = d.get("limit_remaining")
            if lim is not None:
                lim = float(lim)
                out["detail"] += (f"; key limit {d.get('limit_reset') or 'period'} "
                                  f"${lim:,.2f} left")
                if out.get("remaining") is None or lim < out["remaining"]:
                    out["remaining"] = round(lim, 4)
                    out["binding"] = "key limit"
    except httpx.HTTPError:
        pass
    return out


BALANCE_LOOKUP = {"openrouter.ai": _openrouter_balance}

NO_BALANCE_API = {
    "anthropic": "the Anthropic API exposes no balance on a standard key "
                 "(cost_report needs an admin key), so a ceiling is the only "
                 "guard",
    "claude-cli": "a subscription has no balance to read",
}


def balance_for(model) -> dict | None:
    if model.local:
        return None
    why = NO_BALANCE_API.get(model.provider)
    if why:
        return {"provider": model.provider, "unavailable": why}
    base = model.base_url or ""
    for host, fn in BALANCE_LOOKUP.items():
        if host in base:
            key = os.environ.get(model.key_env or "") or ""
            if not key:
                return {"provider": host, "error": f"{model.key_env} not set"}
            return fn(key)
    return {"provider": base or model.provider,
            "unavailable": "no balance endpoint known for this host"}


def balances(models) -> dict:
    out: dict = {}
    seen: dict = {}
    for m in models:
        base = m.base_url or m.provider
        if base in seen:
            out[m.name] = seen[base]
            continue
        b = balance_for(m)
        seen[base] = b
        out[m.name] = b
    return out


def _providers() -> dict:
    from .registry import load_models
    return {m.name: m.provider for m in load_models(include_disabled=True)}


USAGE_KEYS = ("tokens_in", "tokens_out", "cache_read_tokens",
              "cache_write_tokens")


def _peer_usage(td, tid, model, by_provider) -> dict | None:
    rows = []
    for name, e in (td.get(tid) or {}).get("agg", {}).items():
        if name == model.name or by_provider.get(name) != model.provider:
            continue
        if (e or {}).get("tokens_in") is None:
            continue
        rows.append(e)
    if not rows:
        return None
    return {k: sum((r.get(k) or 0) for r in rows) / len(rows)
            for k in USAGE_KEYS}


def _project_task(td, tid, model, by_provider) -> float | None:
    u = _peer_usage(td, tid, model, by_provider)
    if u is None:
        return None
    return model.cost_usd(int(u["tokens_in"]), int(u["tokens_out"]),
                          int(u["cache_read_tokens"]),
                          int(u["cache_write_tokens"]))


def estimate(models, tasks, repeat: int = 1) -> dict:
    from . import report
    td = report.collect_task_data(report.load_all_runs())
    want = {t.id for t in tasks}
    reps = max(1, repeat)
    by_provider = _providers()
    rows = []
    unknown = []
    for m in models:
        billed = not m.local and m.provider != "claude-cli"
        known = projected = 0.0
        priced = modelled = blind = 0
        for tid in want:
            e = (td.get(tid) or {}).get("agg", {}).get(m.name)
            c = (e or {}).get("cost_usd")
            if c is not None:
                known += c
                priced += 1
                continue
            if not billed:
                continue
            p = _project_task(td, tid, m, by_provider)
            if p is None:
                blind += 1
                continue
            projected += p
            modelled += 1
        missing = len(want) - priced
        basis = ("own" if priced and not modelled else
                 "mixed" if priced else
                 "peer" if modelled else "none")
        if billed and blind:
            unknown.append(m.name)
        rows.append({"model": m.name, "priced": priced, "tasks": len(want),
                     "missing": missing, "modelled": modelled, "blind": blind,
                     "basis": basis,
                     "known": round(known * reps, 6),
                     "projected": round(projected * reps, 6),
                     "per_sweep": round(known + projected, 6),
                     "total": round((known + projected) * reps, 6),
                     "local": bool(m.local),
                     "subscription": m.provider == "claude-cli"})
    billed_rows = [r for r in rows
                   if not r["local"] and not r["subscription"]]
    return {"rows": rows,
            "billable": round(sum(r["total"] for r in billed_rows), 4),
            "known": round(sum(r["known"] for r in billed_rows), 4),
            "projected": round(sum(r["projected"] for r in billed_rows), 4),
            "cells": len(want) * len(models) * reps,
            "unpriced_cells": sum(r["missing"] for r in billed_rows) * reps,
            "unknown_models": unknown, "repeat": reps}


def max_spend_usd() -> float | None:
    raw = os.environ.get("MAX_SPEND_USD")
    if raw is None:
        raw = config.load_settings().get("max_spend_usd")
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


class SpendExceeded(Exception):
    pass


class SpendTracker:
    def __init__(self, cap: float | None = None):
        self.cap = cap if cap is not None else max_spend_usd()
        self.spent = 0.0
        self.tripped = False

    def add(self, cost) -> None:
        if not cost or self.cap is None:
            return
        self.spent += float(cost)
        if self.spent > self.cap and not self.tripped:
            self.tripped = True
            raise SpendExceeded(
                f"run stopped: ${self.spent:,.2f} spent, over the "
                f"${self.cap:,.2f} ceiling. Nothing already recorded is lost. "
                f"Raise max_spend_usd in settings.local.json (or set "
                f"MAX_SPEND_USD) to continue.")

    def remaining(self) -> float | None:
        return None if self.cap is None else round(self.cap - self.spent, 4)


def preflight(models, tasks, repeat: int = 1) -> dict:
    est = estimate(models, tasks, repeat)
    bal = balances(models)
    cap = max_spend_usd()
    problems = []
    for m in models:
        b = bal.get(m.name) or {}
        rem = b.get("remaining")
        if rem is None:
            continue
        mine = next((r["total"] for r in est["rows"] if r["model"] == m.name), 0)
        if mine and rem < mine:
            problems.append(
                f"{m.name}: needs about ${mine:,.2f} but {b['provider']} "
                f"reports ${rem:,.2f} available"
                + (f" ({b['binding']})" if b.get("binding") else ""))
    if cap is not None and est["billable"] > cap:
        problems.append(f"estimated ${est['billable']:,.2f} exceeds the "
                        f"${cap:,.2f} ceiling")
    return {"estimate": est, "balances": bal, "cap": cap, "problems": problems}
