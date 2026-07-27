"""A sampling change invalidates the cells that were measured under the old one.

Changing temperature or a sampling knob changes the model's behaviour, so scores
taken before the change are no longer comparable. The /run page surfaces this per
model as a clickable count, and the count must be per CELL: re-running SOME tasks
has to lower it, not clear it. Comparing per RUN got that wrong — a single task
re-run at the new settings made the model look fully up to date while every other
task was still on the old ones.
"""
from harness import config, runner
from harness.registry import Model
from harness.tasks import load_tasks
from harness.util import write_json


def _model(**kw):
    base = dict(name="m1", provider="openai", model="x", base_url="http://x",
                temperature=0.2)
    base.update(kw)
    return Model(**base)


def _cell(tmp_path, run, task_id, sampling_used, model="m1"):
    d = tmp_path / run / model / task_id
    d.mkdir(parents=True, exist_ok=True)
    rec = {"model": model, "task": task_id}
    if sampling_used is not None:
        rec["sampling_used"] = sampling_used
    write_json(d / "metrics.json", rec)


def test_matching_cells_are_current(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path)
    tasks = load_tasks()[:3]
    for t in tasks:
        _cell(tmp_path, "2026-01-01_000000", t.id, {"temperature": 0.2})
    d = runner.sampling_drift([_model()])["m1"]
    assert d["current"] == 3 and d["mismatch"] == 0


def test_a_changed_temperature_marks_those_cells_stale(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path)
    tasks = load_tasks()[:3]
    for t in tasks:
        _cell(tmp_path, "2026-01-01_000000", t.id, {"temperature": 0.2})
    d = runner.sampling_drift([_model(temperature=0.6)])["m1"]
    assert d["mismatch"] == 3
    assert set(d["mismatch_tasks"]) == {t.id for t in tasks}


def test_a_new_sampling_key_marks_cells_stale(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path)
    t0 = load_tasks()[0]
    _cell(tmp_path, "2026-01-01_000000", t0.id, {"temperature": 0.2})
    d = runner.sampling_drift([_model(sampling={"top_p": 0.9})])["m1"]
    assert d["mismatch"] == 1


def test_a_profile_only_affects_the_categories_it_governs(tmp_path, monkeypatch):
    """A coding profile must not invalidate a long-context cell."""
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path)
    code = next(t for t in load_tasks() if t.category == "coding-python")
    ctx = next(t for t in load_tasks() if t.category == "long-context")
    for t in (code, ctx):
        _cell(tmp_path, "2026-01-01_000000", t.id, {"temperature": 0.2})
    m = _model(sampling_profiles={"coding": {"temperature": 0.0}})
    d = runner.sampling_drift([m])["m1"]
    assert d["mismatch_tasks"] == [code.id], d
    assert d["current"] == 1


def test_a_partial_rerun_lowers_the_count_it_does_not_clear_the_flag(tmp_path, monkeypatch):
    """The question this exists to answer: partial progress must be reflected."""
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path)
    tasks = load_tasks()[:6]
    m = _model(temperature=0.6)
    for t in tasks:
        _cell(tmp_path, "2026-01-01_000000", t.id, {"temperature": 0.2})
    assert runner.sampling_drift([m])["m1"]["mismatch"] == 6
    for t in tasks[:2]:
        _cell(tmp_path, "2026-02-01_000000", t.id, {"temperature": 0.6})
    d = runner.sampling_drift([m])["m1"]
    assert d["mismatch"] == 4 and d["current"] == 2
    assert set(d["mismatch_tasks"]) == {t.id for t in tasks[2:]}


def test_cells_predating_the_record_are_unverified_not_mismatched(tmp_path, monkeypatch):
    """Unprovable must not read as wrong, nor as confirmed."""
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path)
    for t in load_tasks()[:3]:
        _cell(tmp_path, "2026-01-01_000000", t.id, None)
    d = runner.sampling_drift([_model()])["m1"]
    assert d["unverified"] == 3 and d["mismatch"] == 0 and d["current"] == 0


def test_tasks_never_run_are_not_counted(tmp_path, monkeypatch):
    """Coverage already reports those; counting them here would double-flag."""
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path)
    assert runner.sampling_drift([_model()])["m1"]["total"] == 0


def test_claude_cli_sampling_is_not_settable(tmp_path, monkeypatch):
    """A value set for a claude-cli model would be DISPLAYED but never sent — the
    same fiction as the old inert `temperature: 0.2`. The flag exists so the page
    and the editor can say so instead of implying it applied."""
    assert _model(provider="claude-cli").sampling_settable is False
    assert _model(provider="openai").sampling_settable is True
