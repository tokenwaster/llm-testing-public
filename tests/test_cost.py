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
