from harness import config, runner
from harness.util import write_json


class _M:
    def __init__(self, name, max_tokens=32768):
        self.name, self.max_tokens = name, max_tokens


def _cell(tmp_path, model, task, attempts, run="2026-01-01_000000"):
    d = tmp_path / run / model / task
    d.mkdir(parents=True, exist_ok=True)
    write_json(d / "metrics.json", {"model": model, "task": task,
                                    "attempts": attempts})


def _att(out, reasoning, kind="runaway", stop="length"):
    return {"n": 1, "tokens_out": out, "reasoning_tokens": reasoning,
            "error_kind": kind, "stop_reason": stop}


def _matrix(tmp_path, monkeypatch, caps=None):
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(runner, "_model_caps",
                        lambda: caps if caps is not None else {"m1": 32768})
    return runner.budget_matrix()


def test_all_budget_spent_reasoning_qualifies(tmp_path, monkeypatch):
    _cell(tmp_path, "m1", "t-001", [_att(32768, 32767)])
    assert _matrix(tmp_path, monkeypatch) == {"m1": ["t-001"]}


def test_a_substantial_answer_does_not_qualify(tmp_path, monkeypatch):
    _cell(tmp_path, "m1", "t-001", [_att(32768, 12000)])
    assert _matrix(tmp_path, monkeypatch) == {}


def test_a_missing_token_count_does_not_qualify(tmp_path, monkeypatch):
    _cell(tmp_path, "m1", "t-001", [_att(None, None)])
    assert _matrix(tmp_path, monkeypatch) == {}
    _cell(tmp_path, "m1", "t-002", [_att(32768, None)])
    assert "t-002" not in _matrix(tmp_path, monkeypatch).get("m1", [])


def test_stopping_short_of_the_ceiling_does_not_qualify(tmp_path, monkeypatch):
    _cell(tmp_path, "m1", "t-001", [_att(1799, 1797)])
    assert _matrix(tmp_path, monkeypatch) == {}


def test_the_ceiling_is_read_from_that_model_s_own_budget(tmp_path, monkeypatch):
    _cell(tmp_path, "m1", "t-001", [_att(1990, 1988)])
    assert _matrix(tmp_path, monkeypatch, caps={"m1": 2048}) == {"m1": ["t-001"]}
    assert _matrix(tmp_path, monkeypatch, caps={"m1": 32768}) == {}


def test_a_non_runaway_cell_never_qualifies(tmp_path, monkeypatch):
    _cell(tmp_path, "m1", "t-001", [_att(32768, 32767, kind=None, stop="stop")])
    assert _matrix(tmp_path, monkeypatch) == {}


def test_the_best_attempt_decides(tmp_path, monkeypatch):
    _cell(tmp_path, "m1", "t-001", [_att(32768, 32767), _att(32768, 10000)])
    assert _matrix(tmp_path, monkeypatch) == {}


def test_reasons_report_the_measurement_not_an_assertion(tmp_path, monkeypatch):
    _cell(tmp_path, "m1", "t-001", [_att(32768, 32766)])
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(runner, "_model_caps", lambda: {"m1": 32768})
    r = runner.budget_reasons()
    assert r["m1"]["t-001"] == "2 of 32,768 tokens went to output"


def test_an_unknown_model_cap_still_admits_on_the_other_evidence(tmp_path,
                                                                 monkeypatch):
    _cell(tmp_path, "m1", "t-001", [_att(32768, 32768)])
    assert _matrix(tmp_path, monkeypatch, caps={}) == {"m1": ["t-001"]}
