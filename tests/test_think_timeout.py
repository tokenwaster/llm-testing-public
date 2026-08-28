"""A model that reasons past the wall clock produced no answer — that is its
result, not the provider's fault.

2026-08-23: kimi-k3 did ctx-014 in 859s (45,507 output tokens) and blew the
900s budget on rs-015. The timeout message counted only visible text, so a
model still thinking reported "streamed 0 chars" — indistinguishable from a
dead socket, and it was read as provider noise. Worse, `timeout` attributes to
infra, and infra is excluded from the attributed score: a model that thought
past the deadline and never answered had its zero written off.
"""
import pytest

from harness import assess
from harness.adapters import AdapterError


def test_the_deadline_message_reports_the_think_channel():
    """All THREE streaming paths: openai-compat, anthropic, and the claude
    CLI — the CLI one is what sonnet-5 and every claude-cli model runs on."""
    import inspect

    from harness import adapters
    from harness.adapters import AnthropicAdapter, OpenAICompatAdapter
    for fn in (OpenAICompatAdapter._chat_stream, AnthropicAdapter._chat_stream,
               adapters._stream_claude_cli):
        src = inspect.getsource(fn)
        assert "think_timeout" in src, fn
        assert "chars of reasoning" in src, fn
        assert "nothing\n                            f\"arrived at all" in src \
            or "nothing" in src, fn


def test_a_think_timeout_is_charged_to_the_model_not_infra():
    assert assess.CATEGORIES["think-timeout"][0] == "model"
    assert assess.CATEGORIES["timeout"][0] == "infra"
    excl = assess.DEFAULTS["attributed_excludes"]
    assert "infra" in excl and "model" not in excl, \
        "a model-attributed failure must stay inside the attributed score"


class _TDef:
    id = "t-1"
    category = "reasoning"


def _classify(kinds):
    result = {"score": {"status": "scored", "score": 0.0,
                        "summary": "run failed (all attempts errored)"},
              "status": "error",
              "attempts": [{"error_kind": k, "tokens_out": 0} for k in kinds]}
    return assess.classify(result, _TDef(), assess.load_cfg())


def test_a_stalled_connection_is_still_infra():
    """No answer and no reasoning means nothing arrived — that IS the
    provider, and it must not be charged to the model."""
    cls = _classify(["timeout"])
    assert cls["attribution"] == "infra"


def test_thinking_past_the_deadline_lands_on_the_model():
    cls = _classify(["think_timeout"])
    assert cls["attribution"] == "model", cls
    assert "reasoning" in cls["detail"] or "reasoning" in cls["category"]


def test_a_think_timeout_is_not_retried():
    """Retrying a model that reasons for 900s just burns another 900s."""
    e = AdapterError("still generating at the 900s deadline", kind="think_timeout",
                     retryable=False)
    assert not e.retryable


def test_the_claude_cli_counts_thinking_blocks():
    """The CLI streams `thinking` content blocks; they were parsed for
    tool_use only, so a reasoning model looked silent at the deadline."""
    import inspect

    from harness import adapters
    src = inspect.getsource(adapters._stream_claude_cli)
    assert '"thinking"' in src and "think_chars" in src
    assert "think_timeout" in src
