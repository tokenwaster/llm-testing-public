
from harness.report import _consistency


def _td(model, per_task):
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
    out = _consistency("m", _td("m", {"t1": (0.4, 2), "t2": (None, 1)}))
    assert out["sigma"] == "±0.400", "the un-repeated task must not dilute it"
    assert out["sigma_note"] == "1 task re-run"


def test_the_least_stable_task_is_named():
    out = _consistency("m", _td("m", {"steady": (0.0, 3), "flaky": (0.47, 3)}))
    assert out["worst"] == "flaky ±0.470"
    assert "flaky ±0.470" in out["sigma_title"]
    assert "steady" not in out["worst"]


def test_a_model_that_never_wavers_reports_zero_not_a_dash():
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
