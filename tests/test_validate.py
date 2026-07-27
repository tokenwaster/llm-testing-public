"""The validator must catch the class of bug that has actually bitten us:
a value declared in a yaml that never reaches the provider.

Each case below is a real defect this suite shipped and found by accident.
"""
from harness.registry import Model
from harness.validate import validate_models


def _m(**kw):
    base = dict(name="m", provider="openai", model="x", base_url="http://x",
                source_file="m.yaml", temperature=0.2)
    base.update(kw)
    return Model(**base)


def _has(problems, *fragments):
    return any(all(f in p for f in fragments) for p in problems)


def test_catches_an_inert_temperature_on_the_claude_cli():
    """The real bug: five claude yamls declared temperature 0.2 for weeks while
    `claude -p` accepted no such flag."""
    p = validate_models([_m(provider="claude-cli", temperature=0.2)])
    assert _has(p, "temperature=0.2", "never sent")


def test_a_null_temperature_on_claude_cli_is_fine():
    assert validate_models([_m(provider="claude-cli", temperature=None)]) == []


def test_catches_sampling_set_where_it_cannot_be_sent():
    """A top_p on a claude model would display on its page and never transmit."""
    p = validate_models([_m(provider="claude-cli", temperature=None,
                            sampling={"top_p": 0.9})])
    assert _has(p, "exposes no sampling flags")


def test_catches_a_typo_in_a_sampling_key():
    """An unknown key is silently dropped at request time, so the yaml would claim
    a setting the model never saw."""
    p = validate_models([_m(sampling={"tempreture": 0.5},
                            sampling_source="https://x")])
    assert _has(p, "unknown sampling key", "tempreture")


def test_catches_an_out_of_range_value():
    p = validate_models([_m(sampling={"top_p": 1.7}, sampling_source="https://x")])
    assert _has(p, "top_p=1.7", "outside the accepted range")


def test_catches_a_non_integer_top_k():
    p = validate_models([_m(sampling={"top_k": 20.5}, sampling_source="https://x")])
    assert _has(p, "top_k", "integer")


def test_catches_a_profile_no_category_maps_to():
    """A profile nothing maps to never applies — it looks configured and is inert."""
    p = validate_models([_m(sampling_profiles={"creative": {"temperature": 1.5}},
                            sampling_source="https://x")])
    assert _has(p, "creative", "never used")


def test_catches_sampling_without_provenance():
    p = validate_models([_m(sampling={"top_p": 0.9})])
    assert _has(p, "sampling_source is empty")


def test_catches_a_non_url_source():
    p = validate_models([_m(sampling={"top_p": 0.9}, sampling_source="the docs")])
    assert _has(p, "must be a URL")


def test_catches_a_zero_max_tokens():
    p = validate_models([_m(max_tokens=0)])
    assert _has(p, "max_tokens must be a positive integer")


def test_catches_a_duplicate_model_name():
    p = validate_models([_m(source_file="a.yaml"), _m(source_file="b.yaml")])
    assert _has(p, "duplicate model name")


def test_the_live_registry_is_clean():
    """Guard: a real yaml edit must not introduce one of the above."""
    assert validate_models() == []



def test_a_model_can_declare_itself_unsettable_on_a_settable_transport():
    assert _m().sampling_settable is True
    assert _m(sampling_settable_yaml=False).sampling_settable is False
    assert _m(provider="claude-cli").sampling_settable is False


def test_a_declared_temperature_on_an_unsettable_model_is_a_problem():
    p = validate_models([_m(sampling_settable_yaml=False, temperature=0.2,
                            sampling_unsettable_reason="takes no sampling")])
    assert _has(p, "temperature=0.2", "takes no sampling", "temperature: null")


def test_sampling_and_profiles_on_an_unsettable_model_are_problems():
    p = validate_models([_m(sampling_settable_yaml=False, temperature=None,
                            sampling_unsettable_reason="takes no sampling",
                            sampling={"top_p": 0.9},
                            sampling_profiles={"coding": {"temperature": 0.0}})])
    assert _has(p, "sampling", "never sent")
    assert _has(p, "sampling_profiles", "never sent")


def test_an_unsettable_claim_needs_a_source():
    """A gateway cannot be asked and will not complain, so the claim rests
    entirely on the model's docs — it has to cite them."""
    p = validate_models([_m(sampling_settable_yaml=False, temperature=None)])
    assert _has(p, "sampling_settable: false", "needs a source")
    ok = validate_models([_m(sampling_settable_yaml=False, temperature=None,
                             sampling_unsettable_reason="reasoning model")])
    assert not _has(ok, "needs a source")


def test_the_reason_is_attributable_not_generic():
    m = _m(sampling_settable_yaml=False, temperature=None,
           sampling_unsettable_reason="takes no temperature or top_p")
    assert m.unsettable_reason == "takes no temperature or top_p"
    assert "Claude CLI" in _m(provider="claude-cli",
                              temperature=None).unsettable_reason
    assert _m().unsettable_reason == ""


def test_nothing_is_transmitted_for_an_unsettable_model():
    """The point of the whole mechanism: the payload must be empty."""
    m = _m(sampling_settable_yaml=False, temperature=None,
           sampling={"top_p": 0.9})
    assert m.sampling_payload("reasoning") == {}


def test_the_yaml_key_is_the_friendly_name(tmp_path):
    """Operators write `sampling_settable: false`; the field is suffixed because a
    property of that name computes the answer when the yaml is silent."""
    from harness.registry import load_models
    (tmp_path / "x.yaml").write_text(
        "name: x\nprovider: openai\nmodel: x\nbase_url: http://x\n"
        "temperature: null\nsampling_settable: false\n"
        "sampling_unsettable_reason: reasoning model\n", encoding="utf-8")
    m = load_models(tmp_path, include_disabled=True)[0]
    assert m.sampling_settable is False
    assert m.unsettable_reason == "reasoning model"
