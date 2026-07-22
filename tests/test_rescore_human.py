"""A rescore must never eat a human's grade.

_rescore writes the whole score record, so without a guard it silently replaces
a verdict formed by watching a render with the checker's number. Clearing the
review on /review is the only way back to the machine's number.
"""

import json

from harness import rescore


def _result(tmp_path, task_id, score_json):
    tdir = tmp_path / "runs" / "2026-01-01_000000" / "m" / task_id
    (tdir / "workspace").mkdir(parents=True)
    (tdir / "workspace" / "app.html").write_text("<html></html>", encoding="utf-8")
    (tdir / "score.json").write_text(json.dumps(score_json), encoding="utf-8")
    (tdir / "metrics.json").write_text(json.dumps(
        {"task": task_id, "model": "m", "status": "ok"}), encoding="utf-8")
    (tdir.parents[1] / "run.json").write_text(json.dumps(
        {"run_id": "2026-01-01_000000", "finished": "2026-01-01T00:00:00Z",
         "models": ["m"], "tasks": []}), encoding="utf-8")
    return tdir


def _run(tmp_path, monkeypatch, task_id="web-012-coin"):
    """Drive _rescore with a checker that always says 0.123."""
    from harness.tasks import Task
    task = Task(id=task_id, category="one-shot-apps", tier=1, title="t",
                path=tmp_path, prompt="p", scoring={"type": "webapp"},
                timeout_s=5, max_retries=0, max_turns=1, checker_timeout_s=5,
                content_hash="h")
    monkeypatch.setattr(rescore.config, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(rescore, "load_tasks", lambda: [task])
    monkeypatch.setattr(rescore.scoring, "run_pytest_checker",
                        lambda t, ws: {"status": "scored", "score": 0.123,
                                       "scored_by": "checker", "summary": "x"})
    monkeypatch.setattr(rescore.report, "generate_all", lambda *a, **k: None)
    return rescore._rescore(task_id, progress=lambda *a: None)


def test_a_human_grade_is_left_alone(tmp_path, monkeypatch):
    tdir = _result(tmp_path, "web-012-coin", {
        "status": "scored", "score": 0.98, "scored_by": "human",
        "machine_score": 0.8, "summary": "human review: 15/15 factors"})
    n = _run(tmp_path, monkeypatch)
    after = json.loads((tdir / "score.json").read_text(encoding="utf-8"))
    assert after["score"] == 0.98, "the human's number must survive a rescore"
    assert after["scored_by"] == "human"
    assert after["machine_score"] == 0.8, "and its audit trail with it"
    assert n == 0, "a preserved result is not a rescored one"


def test_a_machine_score_is_still_rescored(tmp_path, monkeypatch):
    tdir = _result(tmp_path, "web-012-coin", {
        "status": "scored", "score": 0.5, "scored_by": "checker", "summary": "x"})
    n = _run(tmp_path, monkeypatch)
    after = json.loads((tdir / "score.json").read_text(encoding="utf-8"))
    assert after["score"] == 0.123, "checker-scored results must still refresh"
    assert n == 1
