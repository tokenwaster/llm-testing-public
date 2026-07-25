"""Cost pricing, including Anthropic cache pricing for claude-cli.

A subscription (claude-cli) run reports cache-read tokens folded into tokens_in.
Charging every one at the base input rate hugely overstated cache-heavy agentic
runs (a 15-turn task re-reads its context each turn). Model.cost_usd prices a
cache read at 0.1x and a 5-minute cache write at 1.25x the base input rate.
"""
from harness.registry import Model


def _m(inp=10.0, out=50.0):
    return Model(name="m", provider="claude-cli", model="x",
                 pricing={"input_per_mtok": inp, "output_per_mtok": out})


def test_no_cache_args_is_the_plain_formula():
    assert _m().cost_usd(100_000, 2_000) == (100_000 * 10 + 2_000 * 50) / 1e6


def test_missing_tokens_returns_none():
    assert _m().cost_usd(None, 5) is None
    assert _m().cost_usd(5, None) is None


def test_cache_read_priced_at_one_tenth():
    full = _m().cost_usd(100_000, 0)
    cached = _m().cost_usd(100_000, 0, cache_read=100_000)
    assert cached == full * 0.10


def test_cache_write_priced_at_1_25x():
    full = _m().cost_usd(100_000, 0)
    written = _m().cost_usd(100_000, 0, cache_write=100_000)
    assert written == full * 1.25


def test_split_base_read_write():
    c = _m().cost_usd(100_000, 0, cache_read=70_000, cache_write=10_000)
    expect = (20_000 + 70_000 * 0.10 + 10_000 * 1.25) / 1e6 * 10
    assert abs(c - expect) < 1e-12


def test_cache_read_slashes_a_reread_heavy_agentic_run():
    """The bug this fixes: a 236k-input agentic task that is ~90% cache reads
    should cost a fraction of charging all 236k at the base rate."""
    old = _m().cost_usd(236_806, 2_611)
    new = _m().cost_usd(236_806, 2_611, cache_read=int(236_806 * 0.9))
    assert new < old * 0.4



def _cli(cap=32768):
    from types import SimpleNamespace

    from harness.adapters import ClaudeCLIAdapter
    a = ClaudeCLIAdapter.__new__(ClaudeCLIAdapter)
    a.model = SimpleNamespace(model="claude-x", max_tokens=cap)
    return a


def test_claude_over_the_fleet_cap_is_truncated_like_everyone_else():
    """The CLI takes no max_tokens flag, so Claude alone could answer with more
    tokens than the fairness rule grants: sonnet-4-6 scored 1.0 on ctx-013 using
    64,465 tokens — 2x the cap — on a task where hy3 scored 0 for being cut off
    at it. The adapter now applies the budget the way every other provider does,
    so an answer that only appears past the cap is gone."""
    text = ("thinking " * 30000) + "\nANSWER: 42"
    res = _cli()._parse_result(
        {"result": text, "usage": {"input_tokens": 10, "output_tokens": 64465},
         "subtype": "success", "num_turns": 1}, 1.0)
    assert res.tokens_out == 32768, "must be recorded at the cap, not above it"
    assert res.stop_reason == "length", "a ceiling hit, same as any other model"
    assert res.over_cap_tokens == 64465, "the raw count stays auditable"
    assert "ANSWER: 42" not in res.text, "past-the-budget answer must not survive"


def test_claude_under_the_cap_is_untouched():
    res = _cli()._parse_result(
        {"result": "ANSWER: 42", "usage": {"input_tokens": 10, "output_tokens": 500},
         "subtype": "success", "num_turns": 1}, 1.0)
    assert res.text == "ANSWER: 42"
    assert res.tokens_out == 500
    assert res.over_cap_tokens is None
    assert res.stop_reason == "success"


def test_an_over_budget_result_is_not_reported_as_a_clean_pass():
    """It usually IS a pass — that is the problem. It passed on tokens the rule
    does not grant, so it must be attributed to the harness, not the model."""
    from types import SimpleNamespace

    from harness import assess
    res = {"status": "ok",
           "attempts": [{"tokens_out": 32768, "over_cap_tokens": 64465}],
           "score": {"status": "scored", "score": 1.0, "summary": "5/5 passed"}}
    tdef = SimpleNamespace(id="ctx-013", category="long-context",
                           scoring_type="answer", scoring={})
    cls = assess.classify(res, tdef, assess.load_cfg())
    assert cls["category"] == "over-budget", cls
    assert cls["attribution"] == "harness"
