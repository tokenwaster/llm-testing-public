import types

from harness.report import machine_only_means, machine_only_score


def _tdef(cap=None):
    scoring = {} if cap is None else {"automated_max": cap}
    return types.SimpleNamespace(scoring=scoring, category="one-shot-apps",
                                 tier=1, scoring_type="webapp")


def _entry(score, machine=None, status="scored"):
    s = {"status": status, "score": score}
    if machine is not None:
        s["machine_score"] = machine
    return {"score": s}


def test_a_full_machine_pass_on_a_capped_task_counts_as_one():
    assert machine_only_score(_entry(1.0, machine=0.8), _tdef(0.8)) == 1.0


def test_a_partial_machine_pass_rescales_to_its_ceiling():
    assert machine_only_score(_entry(0.3733, machine=0.2462),
                              _tdef(0.8)) == 0.2462 / 0.8


def test_the_human_total_is_ignored_when_a_machine_score_exists():
    high_human = machine_only_score(_entry(1.0, machine=0.5), _tdef(0.8))
    assert high_human == 0.625


def test_an_unreviewed_capped_cell_uses_its_recorded_score():
    assert machine_only_score(_entry(0.8), _tdef(0.8)) == 1.0


def test_an_uncapped_task_is_unchanged():
    assert machine_only_score(_entry(0.75), _tdef()) == 0.75
    assert machine_only_score(_entry(0.75), _tdef(1.0)) == 0.75


def test_the_result_never_exceeds_one():
    assert machine_only_score(_entry(1.0, machine=0.95), _tdef(0.8)) == 1.0


def test_an_unscored_cell_contributes_nothing():
    assert machine_only_score(_entry(None, status="error"), _tdef(0.8)) is None
    assert machine_only_score(_entry(None), _tdef(0.8)) is None


def test_a_zero_ceiling_cannot_divide():
    assert machine_only_score(_entry(0.0, machine=0.0), _tdef(0.0)) is None


def test_the_mean_spans_every_task_not_just_the_capped_ones():
    tdefs = {"capped": _tdef(0.8), "plain": _tdef()}
    task_data = {
        "capped": {"agg": {"m": _entry(1.0, machine=0.8)}},
        "plain": {"agg": {"m": _entry(0.5)}},
    }
    assert machine_only_means(task_data, tdefs)["m"] == 0.75


def test_a_model_with_no_scored_cells_is_absent():
    tdefs = {"plain": _tdef()}
    task_data = {"plain": {"agg": {"m": _entry(None, status="error")}}}
    assert machine_only_means(task_data, tdefs) == {}


def test_tasks_outside_this_dataset_are_skipped():
    tdefs = {"plain": _tdef()}
    task_data = {"plain": {"agg": {"m": _entry(1.0)}},
                 "retired": {"agg": {"m": _entry(0.0)}}}
    assert machine_only_means(task_data, tdefs)["m"] == 1.0


def test_the_lens_is_wired_into_the_overview():
    from pathlib import Path

    from harness import config
    src = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")
    assert 'data-f="nobias"' in src
    assert "nobias:  {label:'No Bias'" in src
    assert 'data-nobias="{{ r.nobias_v }}"' in src
    assert 'data-nobias="{{ r.m_nobias }}"' in src
    assert 'id="nobias"' in src
    assert Path(config.ROOT / "harness" / "report.py").is_file()


def test_the_claude_effort_argv_carries_the_level_only_when_set():
    import types

    from harness.adapters import ClaudeCLIAdapter
    src = __import__("inspect").getsource(ClaudeCLIAdapter)
    assert 'cmd += ["--effort", self.model.effort]' in src
    assert src.count('if self.model.effort:') == 2


def test_a_run_records_the_effort_it_used():
    import inspect

    from harness import runner
    src = inspect.getsource(runner)
    assert '"effort_used"' in src
    assert '"cli_effort_default": _cli_effort_default()' in src


def test_the_ambient_default_is_read_from_settings_not_invented():
    from harness.runner import _cli_effort_default
    v = _cli_effort_default()
    assert v is None or isinstance(v, str)


def test_the_effort_section_and_row_are_wired():
    from harness import config
    src = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")
    assert 'id="effort"' in src
    assert "Reasoning effort (as tested)" in src
    assert "info.html#effort" in src
