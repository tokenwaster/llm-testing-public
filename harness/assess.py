"""Failure & retry assessment — classifies every non-clean result into a
category with an attribution (model | harness | infra | known-limit | clean),
and computes an "attributed score": capability with non-model failures (our
bugs, gateway flakiness) removed.

Diagnosis only; it never changes the raw score. All thresholds live in
directives.yaml `assess:` so the rules are tunable without code changes.

Answer-lane summaries carry "expected 'X', got 'Y'", so the model's answer is
recoverable without re-reading transcripts — that powers the cross-model
suspect-key check.
"""

import re

import yaml

from . import config

DIRECTIVES_FILE = config.ROOT / "directives.yaml"

DEFAULTS = {
    "fleet_budget": 32768,
    "spiral_frac": 0.97,
    "pass_threshold": 0.8,
    "suspect_key_min_models": 2,
    "attributed_excludes": ["harness", "infra"],
}

CATEGORIES = {
    "pass": ("clean", "scored at or above the pass threshold"),
    "partial": ("model", "partial credit — some checks passed, some failed"),
    "wrong-answer": ("model", "produced an answer; it was incorrect"),
    "fell-for-trap": ("model", "gave the memorized classic answer — the "
                      "task's twist changes it (pattern-matched instead of "
                      "reading)"),
    "retrieval-miss": ("model", "found the wrong value in the long context "
                       "(retrieval / recency / aggregation error)"),
    "checker-fail": ("model", "code ran but failed the checker's tests"),
    "infinite-loop": ("model", "the model's code ran too long and the checker "
                      "timed out — almost always an infinite loop"),
    "forbidden-construct": ("model", "used a construct the task forbids "
                            "(e.g. eval / the re or json module)"),
    "rumination-spiral": ("model", "thought until the token budget was gone, "
                          "never produced a usable answer"),
    "incomplete-output": ("model", "answer was cut off when the token budget "
                           "ran out"),
    "format-miss": ("model", "produced output but not in the required format "
                    "(no ANSWER/code/html block)"),
    "agentic-max-turns": ("model", "ran out of agent turns before finishing"),
    "suspect-answer-key": ("harness", "multiple models gave this same answer — "
                           "the answer KEY is the likely fault, not the model"),
    "budget-artifact": ("harness", "hit a token cap BELOW the fleet budget — "
                        "an unfair-budget config bug, re-run before it counts"),
    "checker-error": ("harness", "the checker itself errored (no tests ran) — "
                      "a harness/environment problem, not the model"),
    "transport-drop": ("infra", "the gateway/connection dropped — a flaky "
                       "pipe, not model capability"),
    "rate-limit": ("infra", "provider rate-limited the request"),
    "timeout": ("infra", "the request timed out"),
    "context-overflow": ("known-limit", "prompt exceeded the model's usable "
                         "context window — expected, config-visible"),
    "unknown-error": ("infra", "errored for an unclassified reason"),
}

_GOT = re.compile(r"got '([^']*)'")


def load_cfg() -> dict:
    try:
        data = (yaml.safe_load(DIRECTIVES_FILE.read_text(encoding="utf-8"))
                or {}).get("assess", {})
    except OSError:
        data = {}
    return {**DEFAULTS, **data}


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").strip()).casefold()


def _model_avgs(task_data: dict) -> dict:
    """model -> overall avg score (for the strong-model guard on suspect keys)."""
    acc: dict[str, list] = {}
    for info in task_data.values():
        for model, e in info["agg"].items():
            sc = e.get("score", {})
            if sc.get("status") == "scored" and sc.get("score") is not None:
                acc.setdefault(model, []).append(sc["score"])
    return {m: sum(v) / len(v) for m, v in acc.items() if v}


def suspect_answers(task_data: dict, tdefs: dict, cfg: dict) -> dict:
    """task_id -> {answer, models} where >= N otherwise-strong models (mean
    score >= min_avg) all scored 0 with the SAME answer. The strong-model guard
    separates "the key is wrong" from "weak models share a trap answer".

    Two things make a task immune, because both PROVE the key is answerable:
      * anybody scored above zero on it, and
      * the shared answer is a registered trap.
    Without the first, rs-010 fired as a suspect key while six models were
    answering it correctly - and that verdict is attributed to US, so falling
    for a trap was quietly excluded from the model's attributed score.
    """
    out = {}
    minn = cfg["suspect_key_min_models"]
    min_avg = cfg.get("suspect_key_min_avg", 0.85)
    traps_cfg = cfg.get("traps") or {}
    avgs = _model_avgs(task_data)
    for tid, info in task_data.items():
        tdef = tdefs.get(tid)
        if not tdef or tdef.scoring_type != "answer":
            continue
        if any((e.get("score") or {}).get("status") == "scored"
               and ((e.get("score") or {}).get("score") or 0) > 0
               for e in info["agg"].values()):
            continue
        groups: dict[str, list] = {}
        for model, e in info["agg"].items():
            sc = e.get("score", {})
            if sc.get("status") != "scored" or (sc.get("score") or 0) > 0:
                continue
            m = _GOT.search(sc.get("summary") or "")
            if not m or not m.group(1).strip():
                continue
            groups.setdefault(_norm(m.group(1)), []).append(model)
        best = max(groups.items(), key=lambda kv: len(kv[1]), default=None)
        if not best or len(best[1]) < minn:
            continue
        if _norm(best[0]) in {_norm(t) for t in (traps_cfg.get(tid) or [])}:
            continue
        mean_strength = (sum(avgs.get(m, 0) for m in best[1]) / len(best[1]))
        if mean_strength >= min_avg:
            out[tid] = {"answer": best[0], "models": sorted(best[1]),
                        "strength": round(mean_strength, 3)}
    return out


def classify(result: dict, tdef, cfg: dict, suspect: dict | None = None) -> dict:
    """-> {category, attribution, detail} for one result. `detail` carries
    dynamic specifics (tokens burned, which trap answer, model agreement)."""
    suspect = suspect or {}
    sc = result.get("score") or {}
    score = sc.get("score")
    summary_raw = sc.get("summary") or ""
    summary = summary_raw.lower()
    sdetail = (sc.get("detail") or "").lower()
    attempts = result.get("attempts") or []
    last = attempts[-1] if attempts else {}
    stop = last.get("stop_reason")
    tok_out = last.get("tokens_out") or 0
    errored = result.get("status") != "ok"
    cat = getattr(tdef, "category", "")
    tid = getattr(tdef, "id", None)
    status = str(result.get("status") or "")

    def pack(category, extra=""):
        attr, base = CATEGORIES[category]
        return {"category": category, "attribution": attr,
                "detail": base + (f" — {extra}" if extra else "")}

    if sc.get("status") == "scored" and score is not None \
            and score >= cfg["pass_threshold"]:
        return pack("pass")

    kinds = {a.get("error_kind") for a in attempts if a.get("error_kind")}
    errs = " ".join(str(a.get("error") or "") for a in attempts).lower()
    if any(p in errs for p in (
            "context window", "context length", "context size",
            "maximum context", "available context", "exceeds the context")):
        return pack("context-overflow")
    if "runaway" in kinds or "rumination_spiral" in kinds:
        detail = ("aborted a repetition loop before the token ceiling"
                  if "repetition loop" in errs
                  else (f"burned {tok_out:,} tokens, produced no usable answer"
                        if tok_out else "produced no usable answer"))
        return pack("rumination-spiral", detail)
    if errored and ("connect" in kinds or "transport" in errs
                    or "stream broke" in errs or "peer closed" in errs):
        return pack("transport-drop")
    if errored and ("429" in errs or ("rate" in errs and "limit" in errs)):
        return pack("rate-limit")
    if errored and "timeout" in kinds:
        return pack("timeout")

    if "max_turns" in errs or "max turns" in errs or "max_turns" in status \
            or "max turns" in summary:
        return pack("agentic-max-turns")

    if errored and "format" in kinds and stop != "length":
        return pack("format-miss", "no ANSWER/code/html block in any attempt")

    if stop == "length" and 0 < tok_out < cfg["fleet_budget"] * cfg["spiral_frac"]:
        return pack("budget-artifact",
                    f"hit a {tok_out:,}-token cap (fleet standard is "
                    f"{cfg['fleet_budget']:,})")

    if any(s in sdetail or s in summary for s in
           ("must not use", "forbidden", "eval/exec", "not use eval",
            "must not import", "used a banned")):
        return pack("forbidden-construct")

    if "timed out" in summary:
        return pack("infinite-loop")
    if "no tests ran" in summary or "executable doesn" in summary \
            or "executable doesn" in sdetail:
        return pack("checker-error")

    if getattr(tdef, "scoring_type", "") == "answer":
        gm = _GOT.search(summary_raw)
        got = gm.group(1) if gm else ""
        traps = [_norm(t) for t in (cfg.get("traps") or {}).get(tid, [])]
        if got and _norm(got) in traps:
            return pack("fell-for-trap", f"answered '{got}'")
        sus = suspect.get(tid)
        if sus and got and _norm(got) == sus["answer"]:
            return pack("suspect-answer-key",
                        f"{len(sus['models'])} models gave '{got}'")
        if stop == "length" and "no answer" in summary:
            return pack("rumination-spiral",
                        f"burned {tok_out:,} tokens, produced no ANSWER line")
        if "no answer" in summary:
            return pack("format-miss", "no ANSWER: line in the response")
        if cat == "long-context" and got:
            return pack("retrieval-miss", f"answered '{got}'")
        if got:
            return pack("wrong-answer", f"answered '{got}'")
        if stop == "length":
            return pack("rumination-spiral",
                        f"burned {tok_out:,} tokens, no output")
        return pack("unknown-error")

    if stop == "length":
        if any(s in summary for s in ("no python code", "no html", "run failed")):
            return pack("rumination-spiral",
                        f"burned {tok_out:,} tokens, emitted no usable code")
        return pack("incomplete-output", f"cut off at {tok_out:,} tokens")
    if "no python code" in summary or "no html" in summary:
        return pack("format-miss")
    if score is not None and 0 < score < cfg["pass_threshold"]:
        return pack("partial", summary_raw.replace(" (rescored)", "")[:60])
    if sc.get("status") == "scored":
        return pack("checker-fail", summary_raw.replace(" (rescored)", "")[:60])
    return pack("unknown-error")


def assess_model(model: str, task_data: dict, tdefs: dict,
                 cfg: dict | None = None, suspect: dict | None = None) -> dict:
    """Per-result classifications + rollup for one model, from the
    aggregated-per-task view. Returns {raw_score, attributed_score, n_graded,
    n_attributed, by_attribution, retries:{recovered,fatal,by_kind},
    flagged:[{task, category, attribution, detail, score, retries}]}."""
    cfg = cfg or load_cfg()
    if suspect is None:
        suspect = suspect_answers(task_data, tdefs, cfg)
    excl = set(cfg["attributed_excludes"])

    graded_scores, attributed_scores = [], []
    by_attr: dict[str, int] = {}
    recovered = fatal = 0
    by_kind: dict[str, int] = {}
    flagged = []

    for tid, info in sorted(task_data.items()):
        e = info["agg"].get(model)
        if not e:
            continue
        tdef = tdefs.get(tid)
        cls = classify(e, tdef, cfg, suspect)
        sc = e.get("score") or {}
        scored = sc.get("status") == "scored" and sc.get("score") is not None
        if scored:
            graded_scores.append(sc["score"])
            if cls["attribution"] not in excl:
                attributed_scores.append(sc["score"])

        nret = e.get("n_retries") or 0
        if nret:
            passed = scored and sc["score"] >= cfg["pass_threshold"]
            if passed or e.get("status") == "ok":
                recovered += nret
            else:
                fatal += nret
            for a in (e.get("attempts") or []):
                k = a.get("error_kind")
                if k:
                    by_kind[k] = by_kind.get(k, 0) + 1

        if cls["category"] != "pass":
            by_attr[cls["attribution"]] = by_attr.get(cls["attribution"], 0) + 1
            flagged.append({
                "task": tid, "category": cls["category"],
                "attribution": cls["attribution"], "detail": cls["detail"],
                "score": sc.get("score"), "retries": nret,
                "summary": (sc.get("summary") or "")[:120],
            })

    raw = (sum(graded_scores) / len(graded_scores)) if graded_scores else None
    attr = (sum(attributed_scores) / len(attributed_scores)
            if attributed_scores else None)
    return {
        "raw_score": raw, "attributed_score": attr,
        "n_graded": len(graded_scores), "n_attributed": len(attributed_scores),
        "excluded": len(graded_scores) - len(attributed_scores),
        "by_attribution": by_attr,
        "retries": {"recovered": recovered, "fatal": fatal, "by_kind": by_kind},
        "flagged": flagged,
    }


def assess_run(run: dict, tdefs: dict, cfg: dict | None = None) -> dict:
    """Compact attribution rollup across every result in one run (for the
    run-report header). Uses the run's own results (not the aggregate)."""
    cfg = cfg or load_cfg()
    cohort: dict = {}
    for r in run["results"]:
        cohort.setdefault(r["task"], {"agg": {}})["agg"][r["model"]] = r
    suspect = suspect_answers(cohort, tdefs, cfg)
    by_attr: dict[str, int] = {}
    recovered = fatal = 0
    for r in run["results"]:
        cls = classify(r, tdefs.get(r["task"]), cfg, suspect)
        if cls["category"] != "pass":
            by_attr[cls["attribution"]] = by_attr.get(cls["attribution"], 0) + 1
        nret = r.get("n_retries") or 0
        if nret:
            sc = r.get("score") or {}
            ok = (sc.get("status") == "scored"
                  and (sc.get("score") or 0) >= cfg["pass_threshold"]) \
                or r.get("status") == "ok"
            recovered += nret if ok else 0
            fatal += 0 if ok else nret
    return {"by_attribution": by_attr,
            "retries": {"recovered": recovered, "fatal": fatal}}
