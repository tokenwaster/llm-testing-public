"""The discrimination analysis behind the /discriminate page and the fit
cohort split."""
import types

from harness.registry import infer_family
from harness.report import _pearson, discrimination_stats, family_stats


def test_pearson_needs_overlap_and_variance():
    assert _pearson({"a": 1}, {"a": 1}) is None
    ident = {c: float(i) for i, c in enumerate("abcdefghij")}
    assert _pearson(ident, ident) == 1.0
    flat = {c: 1.0 for c in "abcdefghij"}
    assert _pearson(flat, ident) is None


def _run(results):
    return {"run_id": "r", "results": results}


def _res(model, task, score, cat="reasoning", tier=1, lane="answer"):
    return {"model": model, "task": task, "category": cat, "tier": tier,
            "score": {"status": "scored", "score": score},
            "attempts": [], "tokens_out": 10, "model_meta": {"local": True}}


def test_discrimination_flags_dead_and_frontier_tasks():
    tdefs = {
        "easy": types.SimpleNamespace(tier=1, scoring_type="answer", category="reasoning"),
        "hard": types.SimpleNamespace(tier=1, scoring_type="answer", category="reasoning"),
        "split": types.SimpleNamespace(tier=1, scoring_type="answer", category="reasoning"),
    }
    models = [f"m{i}" for i in range(10)]
    results = []
    for i, m in enumerate(models):
        results.append(_res(m, "easy", 1.0))
        results.append(_res(m, "hard", 0.3))
        results.append(_res(m, "split", 1.0 if i < 5 else 0.0))
    d = discrimination_stats([_run(results)], tdefs)
    flags = {r["tid"]: r["flag"] for r in d["rows"]}
    assert flags["easy"] == "dead"
    assert flags["hard"] == "frontier"
    assert d["n_tasks"] == 3
    assert 0.0 <= d["top_spread"] <= 1.0


def test_infer_family_groups_lineages():
    assert infer_family("gemma-4-12b") == "Gemma"
    assert infer_family("claude-cli-opus-4-8") == "Claude"
    assert infer_family("gpt-oss-20b") == "GPT"
    assert infer_family("qwen3.6-27b") == "Qwen"
    assert infer_family("acme-wonder-7b") == "acme-wonder-7b"


def test_family_stats_groups_and_scores():
    tdefs = {t: types.SimpleNamespace(tier=1, scoring_type="answer",
                                      category="reasoning") for t in ("a", "b")}

    def r(model, sa, sb, local):
        mm = {"local": local}
        return [_res(model, "a", sa) | {"model_meta": mm},
                _res(model, "b", sb) | {"model_meta": mm}]

    results = (r("gemma-4-12b", 0.8, 0.9, True)
               + r("gemma-3-4b", 0.2, 0.4, True)
               + r("claude-cli-opus-4-8", 1.0, 1.0, False))
    fams = family_stats([_run(results)], tdefs)
    assert set(fams) == {"Gemma", "Claude"}
    assert len(fams["Gemma"]) == 2
    assert fams["Gemma"][0]["model"] == "gemma-4-12b"
    assert fams["Gemma"][0]["score"] > fams["Gemma"][1]["score"]
