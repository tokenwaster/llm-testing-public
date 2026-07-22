"""An empty 200 means different things local vs cloud, and mislabelling it
corrupts attribution.

For a LOCAL model (LM Studio) an empty response really is context overflow —
non-retryable, a known limit. For a CLOUD model it is a transient upstream
hiccup: kimi-k3 hit this on a 550-token prompt (nowhere near its window) and got
one un-retried, scored 0.0 that assess then blamed on the model's context. It
must retry, and if it persists attribute to infra — never context-overflow.
"""

import pytest

from harness import assess
from harness.adapters import AdapterError, ChatResult, _reject_degenerate


def _degenerate():
    return ChatResult(text="", total_ms=100.0, tokens_out=None,
                      stop_reason=None, tool_calls=[])


def test_local_empty_is_context_overflow_and_not_retried():
    with pytest.raises(AdapterError) as ei:
        _reject_degenerate(_degenerate(), local=True)
    assert ei.value.retryable is False
    assert "context window" in str(ei.value)


def test_cloud_empty_is_a_retryable_transport_hiccup():
    with pytest.raises(AdapterError) as ei:
        _reject_degenerate(_degenerate(), local=False)
    assert ei.value.retryable is True, "a transient cloud hiccup must get another try"
    assert ei.value.kind == "transport"
    assert "context window" not in str(ei.value), \
        "must not claim a context limit on a model whose window wasn't full"


def test_a_real_response_is_never_rejected():
    good = ChatResult(text="hi", total_ms=1.0, tokens_out=3, stop_reason="stop")
    _reject_degenerate(good, local=False)
    _reject_degenerate(good, local=True)


def test_a_response_with_only_tool_calls_is_not_degenerate():
    from harness.adapters import ToolCall
    r = ChatResult(text="", total_ms=1.0, tokens_out=None, stop_reason=None,
                   tool_calls=[ToolCall(id="1", name="f", args={})])
    _reject_degenerate(r, local=False)


def test_cloud_empty_attributes_to_infra_not_the_model():
    """The whole point: assess must call it transport-drop/infra, not a
    context-overflow known-limit charged against the model."""
    tdef = type("T", (), {"category": "one-shot-apps", "id": "web-007-life",
                          "scoring_type": "webapp"})()
    try:
        _reject_degenerate(_degenerate(), local=False)
    except AdapterError as e:
        result = {"status": "error",
                  "score": {"status": "scored", "score": 0.0, "summary": "run failed"},
                  "attempts": [{"error": str(e), "error_kind": e.kind}]}
    c = assess.classify(result, tdef, assess.load_cfg())
    assert c["category"] == "transport-drop"
    assert c["attribution"] == "infra"


def test_local_empty_still_attributes_to_known_limit():
    tdef = type("T", (), {"category": "long-context", "id": "ctx-008-recall-128k",
                          "scoring_type": "answer"})()
    try:
        _reject_degenerate(_degenerate(), local=True)
    except AdapterError as e:
        result = {"status": "error",
                  "score": {"status": "scored", "score": 0.0, "summary": "run failed"},
                  "attempts": [{"error": str(e), "error_kind": e.kind}]}
    c = assess.classify(result, tdef, assess.load_cfg())
    assert c["category"] == "context-overflow"
    assert c["attribution"] == "known-limit"
