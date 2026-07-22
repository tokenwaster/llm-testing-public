"""A provider rate limit must never be scored as a model failure.

kimi-k3 landed a raw 0.25 while scoring 1.0 on every task it actually reached:
OpenRouter's shared pool was throttling Moonshot, and each 429 was recorded as
score 0.0 "run failed (all attempts errored)". That is the same class of lie the
no-op-floors-at-zero rule exists to prevent - a capability failure on a model
that never got a turn.

The usage-limit path already got this right (drop the task, write no score.json,
let a re-run fill it in). These tests hold the 429 path to the same bar.
"""

import pytest

from harness import runner
from harness.adapters import AdapterError, _classify_http, _retry_after_s



def test_429_is_its_own_kind_and_retryable():
    e = _classify_http(429, '{"error":{"code":429}}', {})
    assert e.kind == "rate_limit", "a 429 must be distinguishable from a 5xx blip"
    assert e.retryable is True


def test_5xx_and_auth_are_unchanged():
    assert _classify_http(503, "boom", {}).kind == "api"
    assert _classify_http(500, "boom", {}).retryable is True
    assert _classify_http(401, "nope", {}).kind == "auth"
    assert _classify_http(401, "nope", {}).retryable is False


def test_retry_after_header_is_honoured():
    assert _retry_after_s({"retry-after": "30"}, "") == 30.0
    assert _retry_after_s({}, "no hint") is None
    assert _retry_after_s({}, '{"reset":1000000000}') is None


def test_real_openrouter_429_body():
    body = ('{"error":{"message":"Provider returned error","code":429,"metadata":'
            '{"raw":"moonshotai/kimi-k3 is temporarily rate-limited upstream. '
            'Please retry shortly, or add your own key","provider_name":'
            '"Moonshot AI","is_byok":false}}}')
    e = _classify_http(429, body, {"retry-after": "20"})
    assert e.kind == "rate_limit"
    assert e.retry_after == 20.0



class _Throttled:
    """An adapter whose provider is always busy."""
    def __init__(self, retry_after=None):
        self.calls = 0
        self.retry_after = retry_after

    def chat(self, *a, **k):
        self.calls += 1
        raise AdapterError("HTTP 429: rate-limited upstream", kind="rate_limit",
                           retryable=True, retry_after=self.retry_after)


class _Broken:
    def chat(self, *a, **k):
        raise AdapterError("HTTP 500: boom", kind="api", retryable=True)


def _runner(tmp_path, adapter, monkeypatch):
    monkeypatch.setattr(runner.time, "sleep", lambda s: None)
    from harness.registry import Model
    m = Model(name="m", provider="openai", model="x", local=False)
    return runner.TaskRunner(tmp_path, m, adapter)


def _task():
    from harness.tasks import Task
    return Task(id="t", category="c", tier=1, title="t", path=None, prompt="p",
                scoring={"type": "answer"}, timeout_s=5, max_retries=1,
                max_turns=1, checker_timeout_s=5, content_hash="h")


def test_exhausted_retries_on_429_raise_rather_than_score_zero(tmp_path, monkeypatch):
    r = _runner(tmp_path, _Throttled(), monkeypatch)
    attempts = []
    with pytest.raises(runner.RateLimited):
        r._chat_with_retries(tmp_path, _task(), [{"role": "user", "content": "x"}],
                             "sys", None, attempts, None)
    assert len(attempts) >= 2, "should have used its retries before unwinding"


def test_a_plain_5xx_still_fails_normally(tmp_path, monkeypatch):
    """Only rate limits get the unscored treatment - a broken provider is still
    a failure the run records."""
    r = _runner(tmp_path, _Broken(), monkeypatch)
    attempts = []
    out = r._chat_with_retries(tmp_path, _task(), [{"role": "user", "content": "x"}],
                               "sys", None, attempts, None)
    assert out is None, "a 5xx must still return None (scored as an error)"


def test_429_waits_what_the_provider_asked(tmp_path, monkeypatch):
    r = _runner(tmp_path, _Throttled(retry_after=25.0), monkeypatch)
    waits = []
    monkeypatch.setattr(runner.time, "sleep", lambda s: waits.append(s))
    with pytest.raises(runner.RateLimited):
        r._chat_with_retries(tmp_path, _task(), [{"role": "user", "content": "x"}],
                             "sys", None, [], None)
    assert waits and all(w == 25.0 for w in waits), \
        f"must honour Retry-After, not the old 2s ramp; got {waits}"


def test_429_without_a_hint_backs_off_properly(tmp_path, monkeypatch):
    r = _runner(tmp_path, _Throttled(), monkeypatch)
    waits = []
    monkeypatch.setattr(runner.time, "sleep", lambda s: waits.append(s))
    with pytest.raises(runner.RateLimited):
        r._chat_with_retries(tmp_path, _task(), [{"role": "user", "content": "x"}],
                             "sys", None, [], None)
    assert waits and waits[0] >= 10, \
        f"the old 2**n burned the whole budget in ~6s; got {waits}"


def test_streak_threshold_exists():
    assert isinstance(runner.RATE_LIMIT_STREAK, int) and runner.RATE_LIMIT_STREAK >= 1
