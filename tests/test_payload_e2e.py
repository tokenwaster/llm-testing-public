import json

import httpx
import pytest

from harness.adapters import ClaudeCLIAdapter, OpenAICompatAdapter
from harness.registry import Model


def _captured(model, category="", monkeypatch=None):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content.decode()))
        return httpx.Response(200, json={
            "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1}})

    transport = httpx.MockTransport(handler)
    real_post = httpx.post

    def fake_post(url, **kw):
        with httpx.Client(transport=transport) as c:
            return c.post(url, **kw)

    monkeypatch.setattr(httpx, "post", fake_post)
    a = OpenAICompatAdapter(model)
    a.task_category = category
    a.model.stream = False
    a.chat([{"role": "user", "content": "hi"}])
    monkeypatch.setattr(httpx, "post", real_post)
    return seen


def _m(**kw):
    base = dict(name="m", provider="openai", model="x",
                base_url="http://example.invalid/v1", stream=False,
                temperature=0.3)
    base.update(kw)
    return Model(**base)


def test_temperature_and_max_tokens_reach_the_wire(monkeypatch):
    body = _captured(_m(max_tokens=4242), monkeypatch=monkeypatch)
    assert body["temperature"] == 0.3
    assert body["max_tokens"] == 4242


def test_configured_sampling_reaches_the_wire(monkeypatch):
    body = _captured(_m(sampling={"top_p": 0.91, "top_k": 7}),
                     monkeypatch=monkeypatch)
    assert body["top_p"] == 0.91 and body["top_k"] == 7


def test_unset_sampling_is_absent_from_the_wire(monkeypatch):
    body = _captured(_m(), monkeypatch=monkeypatch)
    for k in ("top_p", "top_k", "min_p", "seed", "repetition_penalty"):
        assert k not in body, f"{k} should not have been transmitted"


def test_a_null_temperature_is_absent_from_the_wire(monkeypatch):
    body = _captured(_m(temperature=None), monkeypatch=monkeypatch)
    assert "temperature" not in body


def test_the_category_profile_reaches_the_wire(monkeypatch):
    m = _m(temperature=0.7,
           sampling_profiles={"coding": {"temperature": 0.0}})
    body = _captured(m, category="coding-python", monkeypatch=monkeypatch)
    assert body["temperature"] == 0.0
    body2 = _captured(m, category="long-context", monkeypatch=monkeypatch)
    assert body2["temperature"] == 0.7


def test_the_claude_cli_argv_carries_no_sampling(monkeypatch):
    seen = {}

    def fake_stream(cmd, prompt, cwd, timeout_s):
        seen["cmd"] = list(cmd)
        return {"result": "ok", "usage": {"input_tokens": 1, "output_tokens": 1},
                "subtype": "success", "num_turns": 1}

    import harness.adapters as A
    monkeypatch.setattr(A, "_stream_claude_cli", fake_stream)
    monkeypatch.setattr(A.shutil if hasattr(A, "shutil") else A, "__name__", A.__name__)
    m = Model(name="c", provider="claude-cli", model="claude-x", temperature=None)
    a = ClaudeCLIAdapter(m)
    import shutil as _sh
    monkeypatch.setattr(_sh, "which", lambda *_: "claude")
    a.chat([{"role": "user", "content": "hi"}])
    argv = " ".join(seen["cmd"])
    for flag in ("temperature", "top_p", "top_k", "min_p"):
        assert flag not in argv, f"{flag} must not appear in the CLI argv"
