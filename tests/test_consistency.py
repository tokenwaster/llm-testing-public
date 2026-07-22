"""Consistency is measured per task, and it names the culprit.

The old σ was the spread of a model's whole-SUITE average between runs. It is
"—" until a model has two runs — every model in the v0.6 dataset showed "—" —
and once a model does have two, a partial re-run of 5 hard tasks gets compared
against a 42-task pass and the difference is reported as "inconsistency".

Spread only means something against the same task, which is also the only way to
answer the question worth asking: WHICH task is unstable.
"""

from harness.report import _consistency


def _td(model, per_task):
    """per_task: {task_id: (score_sigma, n_runs)}"""
    return {tid: {"agg": {model: {"score_sigma": sg, "n_runs": n}}}
            for tid, (sg, n) in per_task.items()}


def test_nothing_repeated_reports_no_spread():
    out = _consistency("m", _td("m", {"t1": (None, 1), "t2": (None, 1)}))
    assert out["sigma"] == "—"
    assert out["worst"] == "—"
    assert "no task re-run yet" in out["sigma_note"]
    assert "--repeat" in out["sigma_title"], "say how to get the data"


def test_sigma_is_the_mean_of_the_per_task_sigmas():
    out = _consistency("m", _td("m", {"t1": (0.5, 3), "t2": (0.1, 3)}))
    assert out["sigma"] == "±0.300"
    assert out["sigma_note"] == "2 tasks re-run"


def test_a_task_run_once_is_not_counted_as_stable():
    """It has no spread — that is different from having zero spread."""
    out = _consistency("m", _td("m", {"t1": (0.4, 2), "t2": (None, 1)}))
    assert out["sigma"] == "±0.400", "the un-repeated task must not dilute it"
    assert out["sigma_note"] == "1 task re-run"


def test_the_least_stable_task_is_named():
    out = _consistency("m", _td("m", {"steady": (0.0, 3), "flaky": (0.47, 3)}))
    assert out["worst"] == "flaky ±0.470"
    assert "flaky ±0.470" in out["sigma_title"]
    assert "steady" not in out["worst"]


def test_a_model_that_never_wavers_reports_zero_not_a_dash():
    """Run 3× and always 1.0 is a finding; it must not look un-measured."""
    out = _consistency("m", _td("m", {"t1": (0.0, 3), "t2": (0.0, 3)}))
    assert out["sigma"] == "±0.000"
    assert out["sigma_note"] == "2 tasks re-run"
    assert out["worst"] == "—", "nothing moved, so no culprit"
    assert "identically" in out["sigma_title"]


def test_other_models_do_not_leak_in():
    td = {"t1": {"agg": {"me": {"score_sigma": 0.1, "n_runs": 2},
                         "them": {"score_sigma": 0.9, "n_runs": 2}}}}
    assert _consistency("me", td)["sigma"] == "±0.100"
    assert _consistency("them", td)["sigma"] == "±0.900"


def test_a_model_absent_from_a_task_is_skipped():
    td = {"t1": {"agg": {"other": {"score_sigma": 0.9, "n_runs": 2}}},
          "t2": {"agg": {"me": {"score_sigma": 0.2, "n_runs": 2}}}}
    assert _consistency("me", td)["sigma"] == "±0.200"


def test_sort_key_is_numeric_and_sorts_dashes_last():
    none = _consistency("m", _td("m", {"t1": (None, 1)}))
    some = _consistency("m", _td("m", {"t1": (0.25, 2)}))
    assert none["sigma_sort"] == "", "empty sorts last in the table sorter"
    assert float(some["sigma_sort"]) == 0.25


def test_the_tooltip_lists_at_most_five_offenders():
    out = _consistency("m", _td("m", {f"t{i}": (0.1 * (i + 1), 2)
                                      for i in range(8)}))
    assert out["sigma_title"].count(";") == 4, "5 listed, so 4 separators"
