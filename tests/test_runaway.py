"""Runaway-generation handling: a model that hits its token ceiling without
ever producing an answer (a bad quant looping, or ruminating forever).

Covers the four fixes:
  1. the retry loop caps length-runaways at ONE retry (not task.max_retries)
  2. results carry a `failure_mode` and reports badge it distinctly
  3. the streaming adapter aborts a tight repetition loop mid-stream
  4. reasoning tokens are never mistaken for the answer (fairness)
"""
import types
from pathlib import Path

import pytest

from harness import adapters, runner
from harness.adapters import AdapterError, ChatResult, _LoopGuard



def test_loop_guard_trips_on_a_tight_cycle():
    g = _LoopGuard()
    tripped = any(g.feed("ab") for _ in range(600))
    assert tripped


def test_loop_guard_trips_on_a_repeated_sentence():
    g = _LoopGuard()
    sent = ("I cannot determine the answer without more context so let me "
            "reconsider the whole problem again from the very beginning now. ")
    assert any(g.feed(sent) for _ in range(60))


def test_loop_guard_ignores_varied_prose():
    g = _LoopGuard()
    prose = ("The quick brown fox jumps over the lazy dog while a benchmark "
             "harness scores many different models on many different tasks. ")
    assert not any(g.feed(prose + str(i)) for i in range(200))



class _FakeAdapter:
    """Returns a fixed ChatResult every call; counts calls."""
    def __init__(self, res):
        self.res = res
        self.calls = 0

    def chat(self, messages, system=None, tools=None, timeout_s=180):
        self.calls += 1
        return self.res


def _runner(tmp_path, res):
    model = types.SimpleNamespace(name="m", provider="openai", local=True)
    return runner.TaskRunner(tmp_path, model, _FakeAdapter(res))


def _task(max_retries=3):
    return types.SimpleNamespace(id="t", max_retries=max_retries, timeout_s=60)


def test_length_runaway_is_capped_at_one_retry(tmp_path):
    """A response that hit the token CEILING and fails validation must not be
    retried task.max_retries times — one retry, then stop (2 attempts total)."""
    res = ChatResult(text="", total_ms=1.0, ttft_ms=1.0, tokens_in=10,
                     tokens_out=32768, stop_reason="length")
    r = _runner(tmp_path, res)
    (tmp_path / "m" / "t").mkdir(parents=True)
    attempts = []
    out = r._chat_with_retries(
        tmp_path / "m" / "t", _task(max_retries=3),
        [{"role": "user", "content": "hi"}], "", None, attempts,
        validate=lambda x: "no ANSWER: line in response")
    assert out is None
    assert len(attempts) == 2, "runaway should stop after one retry"
    assert attempts[-1]["error_kind"] == "runaway"


def test_plain_format_miss_still_uses_full_retries(tmp_path):
    """A model that STOPPED normally but formatted wrong isn't a runaway — it
    gets the full retry budget (the model might format correctly next time)."""
    res = ChatResult(text="here you go", total_ms=1.0, ttft_ms=1.0,
                     tokens_in=10, tokens_out=50, stop_reason="stop")
    r = _runner(tmp_path, res)
    (tmp_path / "m" / "t").mkdir(parents=True)
    attempts = []
    r._chat_with_retries(
        tmp_path / "m" / "t", _task(max_retries=3),
        [{"role": "user", "content": "hi"}], "", None, attempts,
        validate=lambda x: "no ANSWER: line in response")
    assert len(attempts) == 4, "first try + 3 retries"
    assert attempts[-1]["error_kind"] == "format"



def test_failure_mode_flags_a_length_runaway():
    atts = [{"stop_reason": "length", "error_kind": "runaway"}]
    assert runner._failure_mode(atts, "ok") == "runaway"


def test_failure_mode_not_flagged_for_a_truncated_but_graded_answer():
    atts = [{"stop_reason": "length", "error_kind": None}]
    assert runner._failure_mode(atts, "ok") is None


def test_failure_mode_none_when_last_attempt_succeeded():
    atts = [{"stop_reason": "length"}, {"stop_reason": "stop", "error_kind": None}]
    assert runner._failure_mode(atts, "ok") is None


def test_report_derivation_gates_runaway_on_a_failing_score():
    """Old runs (no error_kind='runaway'): a ceiling-hit that graded 0 is a
    runaway; one that still scored is only truncated."""
    from harness.report import _failure_mode_of
    ran = {"attempts": [{"stop_reason": "length"}],
           "score": {"status": "scored", "score": 0.0}}
    trunc = {"attempts": [{"stop_reason": "length"}],
             "score": {"status": "scored", "score": 0.8}}
    assert _failure_mode_of(ran) == "runaway"
    assert _failure_mode_of(trunc) is None


def test_fail_badge_shows_runaway_but_not_on_a_full_pass():
    from harness.report import _fail_badge
    failed = {"failure_mode": "runaway", "score": {"status": "scored", "score": 0.0}}
    assert "runaway" in _fail_badge(failed)
    passed = {"failure_mode": "max_turns", "score": {"status": "scored", "score": 1.0}}
    assert _fail_badge(passed) == ""



class _FakeStream:
    def __init__(self, lines):
        self._lines = lines
        self.status_code = 200
        self.text = ""

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return b""

    def iter_lines(self):
        yield from self._lines


def test_reasoning_tokens_captured_from_usage(monkeypatch):
    """A model that spends its budget thinking must record reasoning tokens, so a
    'ruminated it all away' zero reads differently from an 'empty content' one."""
    import json
    from harness.registry import Model
    lines = [
        'data: ' + json.dumps({"choices": [{"delta": {"reasoning_content": "hmm "}}]}),
        'data: ' + json.dumps({"choices": [{"delta": {}, "finish_reason": "length"}],
                               "usage": {"completion_tokens": 32768,
                                         "completion_tokens_details": {"reasoning_tokens": 32000}}}),
        'data: [DONE]',
    ]
    monkeypatch.setattr(adapters.httpx, "stream", lambda *a, **k: _FakeStream(lines))
    ad = adapters.OpenAICompatAdapter(
        Model(name="m", provider="openai", model="x",
              base_url="http://localhost:1234/v1", local=True))
    res = ad._chat_stream({"model": "x", "messages": []}, timeout_s=60)
    assert res.reasoning_tokens == 32000
    assert res.text == ""


def test_reasoning_tokens_estimated_when_usage_omits_them(monkeypatch):
    """Provider streamed a think channel but didn't count it in usage — estimate
    from the streamed chars so the signal isn't lost."""
    import json
    from harness.registry import Model
    lines = [
        'data: ' + json.dumps({"choices": [{"delta": {"reasoning_content": "x" * 400}}]}),
        'data: ' + json.dumps({"choices": [{"delta": {}, "finish_reason": "length"}],
                               "usage": {"completion_tokens": 100}}),
        'data: [DONE]',
    ]
    monkeypatch.setattr(adapters.httpx, "stream", lambda *a, **k: _FakeStream(lines))
    ad = adapters.OpenAICompatAdapter(
        Model(name="m", provider="openai", model="x",
              base_url="http://localhost:1234/v1", local=True))
    res = ad._chat_stream({"model": "x", "messages": []}, timeout_s=60)
    assert res.reasoning_tokens == 100


def test_reasoning_content_is_excluded_from_the_answer(monkeypatch):
    """The whole fairness question behind the QAT zeros: a model that spends its
    budget in the THINK channel and emits no answer content must yield empty
    answer text (→ scores 0 as 'no answer'), never have its reasoning graded."""
    import json
    from harness.registry import Model

    lines = [
        'data: ' + json.dumps({"choices": [{"delta": {"reasoning_content": "let me think... "}}]}),
        'data: ' + json.dumps({"choices": [{"delta": {"reasoning_content": "still thinking "}}]}),
        'data: ' + json.dumps({"choices": [{"delta": {},
                              "finish_reason": "length"}], "usage": {"completion_tokens": 32768}}),
        'data: [DONE]',
    ]
    monkeypatch.setattr(adapters.httpx, "stream",
                        lambda *a, **k: _FakeStream(lines))
    model = Model(name="m", provider="openai", model="x",
                  base_url="http://localhost:1234/v1", local=True)
    ad = adapters.OpenAICompatAdapter(model)
    res = ad._chat_stream({"model": "x", "messages": []}, timeout_s=60)
    assert res.text == "", "reasoning must not leak into the answer text"
    assert res.stop_reason == "length"
    from harness import scoring
    tdef = types.SimpleNamespace(scoring={"answer": "42", "match": "exact"})
    assert scoring.score_answer(tdef, res.text)["score"] == 0.0
