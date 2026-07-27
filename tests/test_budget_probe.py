"""Which cells the TOKEN BUDGET silenced — as opposed to the model failing.

A thinking model can spend its whole output budget in the think channel and emit
almost nothing a checker can read. Measured on agents-a1: 32,766-32,768 of 32,768
tokens reasoning, 1-2 tokens of answer, six attempts running. Scoring that 0.0
records "cannot do the task" when what was observed is "was not given room to say
so", so those cells get a probe at a raised budget in special/.

Qualification has to be strict, and every loosening here was a real false positive
found on the live data:

  * treating a MISSING token count as zero visible tokens admitted 20 cells across
    9 models on no evidence at all — unknown is not muted;
  * accepting `stop_reason == "length"` alone admitted qwen3-32b at 1,799 tokens,
    which had filled its loaded CONTEXT window, not its budget — a bigger budget
    cannot fix that, a bigger window can.
"""
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
    """The agents-a1 shape: ceiling reached, essentially no visible answer."""
    _cell(tmp_path, "m1", "t-001", [_att(32768, 32767)])
    assert _matrix(tmp_path, monkeypatch) == {"m1": ["t-001"]}


def test_a_substantial_answer_does_not_qualify(tmp_path, monkeypatch):
    """A runaway that DID answer is a loop or a clipped reply — more budget feeds
    the loop rather than fixing it."""
    _cell(tmp_path, "m1", "t-001", [_att(32768, 12000)])
    assert _matrix(tmp_path, monkeypatch) == {}


def test_a_missing_token_count_does_not_qualify(tmp_path, monkeypatch):
    """Unknown is not muted. Coercing null to 0 admitted 20 cells on no evidence."""
    _cell(tmp_path, "m1", "t-001", [_att(None, None)])
    assert _matrix(tmp_path, monkeypatch) == {}
    _cell(tmp_path, "m1", "t-002", [_att(32768, None)])
    assert "t-002" not in _matrix(tmp_path, monkeypatch).get("m1", [])


def test_stopping_short_of_the_ceiling_does_not_qualify(tmp_path, monkeypatch):
    """qwen3-32b stopped at "length" after 1,799 of 32,768 tokens because PROMPT +
    output filled the loaded window. The remedy is a bigger window, not a bigger
    budget, so it must not land in this probe set."""
    _cell(tmp_path, "m1", "t-001", [_att(1799, 1797)])
    assert _matrix(tmp_path, monkeypatch) == {}


def test_the_ceiling_is_read_from_that_model_s_own_budget(tmp_path, monkeypatch):
    """The threshold is relative: the same 1,990 tokens is a ceiling hit for a model
    budgeted 2,048 and nowhere near one for a model budgeted 32,768."""
    _cell(tmp_path, "m1", "t-001", [_att(1990, 1988)])
    assert _matrix(tmp_path, monkeypatch, caps={"m1": 2048}) == {"m1": ["t-001"]}
    assert _matrix(tmp_path, monkeypatch, caps={"m1": 32768}) == {}


def test_a_non_runaway_cell_never_qualifies(tmp_path, monkeypatch):
    _cell(tmp_path, "m1", "t-001", [_att(32768, 32767, kind=None, stop="stop")])
    assert _matrix(tmp_path, monkeypatch) == {}


def test_the_best_attempt_decides(tmp_path, monkeypatch):
    """A cell that spoke on ANY attempt was not silenced."""
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
    """A model with no yaml (a historical name) has no cap to compare against; the
    visible-token evidence still stands on its own."""
    _cell(tmp_path, "m1", "t-001", [_att(32768, 32768)])
    assert _matrix(tmp_path, monkeypatch, caps={}) == {"m1": ["t-001"]}
