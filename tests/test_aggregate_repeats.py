"""Testing a model·task twice in a dataset fleshes the number out.

The score is the MEAN of every scored run, not the newest. Latest-wins made a
re-run replace what came before, so three trials of 1.0/0.5/0.0 reported 0.0 —
one sample, worst purely by run order — while the σ column described the spread
of three samples the headline had thrown away.

Unscored runs (crash, spiral, DNF) stay out of the mean, matching _summarize,
which counts only status=="scored" toward a model's average.
"""

import pytest

from harness.report import _aggregate, _runs_badge, collect_task_data


def _entry(run_id, score, status="scored", **kw):
    sc = {"status": status} if score is None else {"status": status, "score": score,
                                                   "summary": f"s={score}"}
    return {"task": "t1", "model": "m1", "category": "reasoning", "tier": 1,
            "run_id": run_id, "status": "ok", "score": sc, "attempts": [],
            "wall_ms": kw.get("wall_ms", 100), "tokens_in": kw.get("tokens_in", 10),
            "tokens_out": kw.get("tokens_out", 10), "cost_usd": kw.get("cost_usd", 1.0),
            "n_retries": kw.get("n_retries", 0), "gen_tokens_per_sec": 50.0}


def _run(run_id, entries):
    return {"run_id": run_id, "manifest": {}, "results": entries}



def test_one_run_is_unchanged():
    """The whole existing dataset is n=1; the mean of one value is that value."""
    agg = _aggregate([_entry("r1", 0.75)])
    assert agg["score"]["score"] == 0.75
    assert agg["n_runs"] == 1
    assert agg["n_scored"] == 1, "n_scored is always present, even for one run"
    assert agg["score_sigma"] is None



def test_runs_badge_hidden_for_a_single_run():
    assert _runs_badge(1, 1, ["r1"]) == ("", "")


def test_runs_badge_plain_when_every_run_scored():
    badge, title = _runs_badge(3, 3, ["a", "b", "c"])
    assert badge == "×3"
    assert "mean of 3 runs" in title


def test_runs_badge_shows_scored_over_total_when_some_didnt_score():
    """The mean is over the SCORED runs only, so ×2/3 must not imply all 3
    counted toward the number."""
    badge, title = _runs_badge(3, 2, ["a", "b", "c"])
    assert badge == "×2/3"
    assert "2 scored of 3 runs" in title and "1 unscored" in title


def test_three_runs_average_rather_than_replace():
    agg = _aggregate([_entry("r1", 1.0), _entry("r2", 0.5), _entry("r3", 0.0)])
    assert agg["score"]["score"] == 0.5, "the mean, not the newest (0.0)"
    assert agg["n_runs"] == 3
    assert agg["n_scored"] == 3


def test_a_fourth_run_moves_the_aggregate_again():
    """'Test more than once and it just keeps fleshing out the aggregate.'"""
    three = _aggregate([_entry("r1", 1.0), _entry("r2", 1.0), _entry("r3", 1.0)])
    four = _aggregate([_entry("r1", 1.0), _entry("r2", 1.0), _entry("r3", 1.0),
                       _entry("r4", 0.0)])
    assert three["score"]["score"] == 1.0
    assert four["score"]["score"] == 0.75
    assert four["n_runs"] == 4


def test_order_does_not_matter():
    a = _aggregate([_entry("r1", 0.0), _entry("r2", 1.0)])
    b = _aggregate([_entry("r1", 1.0), _entry("r2", 0.0)])
    assert a["score"]["score"] == b["score"]["score"] == 0.5


def test_sigma_reports_the_spread():
    agg = _aggregate([_entry("r1", 1.0), _entry("r2", 1.0), _entry("r3", 1.0)])
    assert agg["score_sigma"] == 0.0, "a model that never wavers"
    wobbly = _aggregate([_entry("r1", 1.0), _entry("r2", 0.0)])
    assert wobbly["score_sigma"] == 0.5



def test_an_unscored_run_stays_out_of_the_mean():
    """_summarize excludes status!="scored" from a model's average, so a failed
    trial must not silently become a 0 here when it isn't one there."""
    agg = _aggregate([_entry("r1", 1.0), _entry("r2", None, status="error")])
    assert agg["score"]["score"] == 1.0
    assert agg["n_scored"] == 1
    assert agg["n_runs"] == 2, "but the run still counts as having happened"


def test_all_runs_unscored_keeps_the_failure_visible():
    agg = _aggregate([_entry("r1", None, status="error"),
                      _entry("r2", None, status="error")])
    assert agg["score"].get("score") is None
    assert agg["score_sigma"] is None


def test_the_newest_scored_record_supplies_the_prose():
    agg = _aggregate([_entry("r1", 1.0), _entry("r2", 0.0)])
    assert agg["score"]["summary"] == "s=0.0", "newest record's prose"
    assert agg["score"]["score"] == 0.5, "but the aggregated number"



def test_cost_and_wall_average_so_a_retest_is_not_more_expensive():
    """Re-testing must not make a model look slower or pricier: these describe
    ONE pass, so they mean rather than accumulate."""
    agg = _aggregate([_entry("r1", 1.0, cost_usd=2.0, wall_ms=100),
                      _entry("r2", 1.0, cost_usd=4.0, wall_ms=300)])
    assert agg["cost_usd"] == 3.0
    assert agg["wall_ms"] == 200


def test_run_ids_are_all_recorded():
    agg = _aggregate([_entry("r1", 1.0), _entry("r2", 1.0)])
    assert agg["run_ids"] == ["r1", "r2"]
    assert agg["run_id"] == "r2", "newest, for links to files/transcript"



def test_collect_task_data_aggregates_across_runs():
    runs = [_run("r1", [_entry("r1", 1.0)]),
            _run("r2", [_entry("r2", 0.0)])]
    td = collect_task_data(runs)
    assert td["t1"]["agg"]["m1"]["score"]["score"] == 0.5
    assert td["t1"]["agg"]["m1"]["n_runs"] == 2
    assert len(td["t1"]["history"]) == 2, "history keeps every run"


def test_separate_models_do_not_mix():
    e2 = {**_entry("r1", 0.0), "model": "m2"}
    td = collect_task_data([_run("r1", [_entry("r1", 1.0), e2])])
    assert td["t1"]["agg"]["m1"]["score"]["score"] == 1.0
    assert td["t1"]["agg"]["m2"]["score"]["score"] == 0.0


@pytest.mark.parametrize("scores,expect", [
    ([1.0], 1.0), ([1.0, 1.0], 1.0), ([1.0, 0.0], 0.5),
    ([0.9, 0.8, 0.7], pytest.approx(0.8)),
])
def test_means(scores, expect):
    agg = _aggregate([_entry(f"r{i}", s) for i, s in enumerate(scores)])
    assert agg["score"]["score"] == expect
