
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
    from harness.tasks import Task
    task = Task(id=task_id, category="one-shot-apps", tier=1, title="t",
                path=tmp_path, prompt="p", scoring={"type": "webapp"},
                timeout_s=5, max_retries=0, max_turns=1, checker_timeout_s=5,
                content_hash="h")
    monkeypatch.setattr(rescore.config, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(rescore, "load_tasks", lambda **kw: [task])
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


def test_over_budget_overrides_even_a_human_grade(tmp_path, monkeypatch):
    from harness import config, rescore
    from harness.util import read_json, write_json

    run = tmp_path / "runs" / "r1"
    cell = run / "claude-cli-x" / "web-012-coin"
    (cell / "workspace").mkdir(parents=True)
    write_json(run / "run.json", {"run_id": "r1", "finished": "now"})
    write_json(cell / "metrics.json", {
        "status": "ok", "attempts": [{"tokens_out": 32768,
                                      "over_cap_tokens": 33774}]})
    write_json(cell / "score.json", {"status": "scored", "score": 1.0,
                                     "scored_by": "human"})
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(rescore, "_active_run", lambda: None)
    monkeypatch.setattr(rescore.report, "generate_all", lambda *a, **k: None)

    rescore._rescore("*", progress=lambda *_: None)

    out = read_json(cell / "score.json", {})
    assert out["score"] == 0.0, "an over-budget cell must not keep a human pass"
    assert out["scored_by"] == "harness"
    assert out["voided_human_score"] == 1.0, "the voided grade stays on record"
