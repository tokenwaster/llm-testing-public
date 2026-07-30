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



def _m2(**kw):
    from harness.registry import Model
    base = dict(name="m", provider="openai", model="x", base_url="http://x")
    base.update(kw)
    return Model(**base)


def test_unset_sampling_keys_are_never_transmitted():
    p = _m2(temperature=0.2).sampling_payload()
    assert p == {"temperature": 0.2}, p


def test_a_null_temperature_is_omitted_not_sent_as_null():
    assert _m2(temperature=None).sampling_payload() == {}


def test_configured_sampling_is_forwarded():
    p = _m2(temperature=0.6,
            sampling={"top_p": 0.95, "top_k": 20, "min_p": 0.0}).sampling_payload()
    assert p == {"temperature": 0.6, "top_p": 0.95, "top_k": 20, "min_p": 0.0}


def test_unknown_sampling_keys_are_ignored():
    p = _m2(temperature=0.2, sampling={"tempreture": 9, "top_p": 0.9}).sampling_payload()
    assert "tempreture" not in p
    assert p["top_p"] == 0.9



def _prof_model(**kw):
    from harness.registry import Model
    base = dict(name="m", provider="openai", model="x", base_url="http://x",
                temperature=0.7, sampling={"top_p": 0.8, "top_k": 20},
                sampling_profiles={"reasoning": {"temperature": 0.6, "top_p": 0.95},
                                   "coding": {"temperature": 0.0}})
    base.update(kw)
    return Model(**base)


def test_a_category_draws_from_its_mapped_profile():
    m = _prof_model()
    assert m.sampling_payload("coding-python")["temperature"] == 0.0
    assert m.sampling_payload("reasoning")["temperature"] == 0.6
    assert m.sampling_payload("long-context")["temperature"] == 0.7


def test_profile_overlays_base_rather_than_replacing_it():
    p = _prof_model().sampling_payload("coding-python")
    assert p == {"temperature": 0.0, "top_p": 0.8, "top_k": 20}, p


def test_an_unmapped_category_falls_back_to_base():
    m = _prof_model()
    assert m.resolved_sampling("no-such-category")[1] == ""
    assert m.sampling_payload("no-such-category")["temperature"] == 0.7


def test_a_model_with_no_profiles_is_unaffected_by_category():
    m = _prof_model(sampling_profiles={})
    a = m.sampling_payload("coding-python")
    b = m.sampling_payload("long-context")
    assert a == b


def test_only_temperature_set_means_everything_else_is_provider_default():
    from harness.registry import Model
    m = Model(name="t", provider="openai", model="x", base_url="http://x",
              temperature=0.6)
    assert m.sampling_payload("coding-python") == {"temperature": 0.6}


def test_the_resolved_profile_name_is_reported_for_the_record():
    assert _prof_model().resolved_sampling("math")[1] == "reasoning"
    assert _prof_model().resolved_sampling("agentic")[1] == "coding"
