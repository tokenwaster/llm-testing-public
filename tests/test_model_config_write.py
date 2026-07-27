"""Writing a model yaml from the operator page must not destroy what is around it.

Every configuration bug this suite has shipped was a value that did not reach the
provider it was written for, so the write path is worth testing directly: the
comments in a model yaml are the record of WHY a value is what it is (max_tokens
carries "uniform thinking budget across all local models (fairness)"), and a save
that silently drops them loses the reason while keeping the number.
"""
import textwrap

import yaml

from harness.registry import set_yaml_key

SRC = textwrap.dedent("""\
    # Auto-registered from LM Studio
    name: m1
    provider: openai
    max_tokens: 32768   # uniform thinking budget across all local models (fairness)
    context_length: 32768  # NATIVE window limit
    temperature: 0.2
    enabled: true
    """)


def _write(tmp_path):
    p = tmp_path / "m1.yaml"
    p.write_text(SRC, encoding="utf-8")
    return p


def test_the_edited_lines_own_comment_survives(tmp_path):
    p = _write(tmp_path)
    set_yaml_key(p, "max_tokens", "65536")
    text = p.read_text(encoding="utf-8")
    assert "max_tokens: 65536" in text
    assert "uniform thinking budget" in text, \
        "the edited line's comment was dropped — the reason for the value is gone"
    assert yaml.safe_load(text)["max_tokens"] == 65536


def test_other_lines_are_untouched(tmp_path):
    p = _write(tmp_path)
    set_yaml_key(p, "temperature", "0.6")
    text = p.read_text(encoding="utf-8")
    assert "# Auto-registered from LM Studio" in text
    assert "NATIVE window limit" in text
    assert yaml.safe_load(text) == {"name": "m1", "provider": "openai",
                                    "max_tokens": 32768, "context_length": 32768,
                                    "temperature": 0.6, "enabled": True}


def test_a_hash_inside_a_value_is_not_treated_as_a_comment(tmp_path):
    """YAML only starts a comment after whitespace, and sampling_source is a URL —
    a fragment must not be mistaken for one and re-attached to the next value."""
    p = _write(tmp_path)
    set_yaml_key(p, "sampling_source", "https://example.invalid/docs#sampling")
    set_yaml_key(p, "sampling_source", "https://example.invalid/other")
    assert yaml.safe_load(p.read_text(encoding="utf-8"))["sampling_source"] == \
        "https://example.invalid/other"


def test_an_inline_mapping_round_trips(tmp_path):
    """sampling and sampling_profiles are written as one inline mapping line."""
    p = _write(tmp_path)
    set_yaml_key(p, "sampling", "{ top_p: 0.95, top_k: 20 }")
    set_yaml_key(p, "sampling_profiles",
                 "{ reasoning: { temperature: 0.6, top_p: 0.95 } }")
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert d["sampling"] == {"top_p": 0.95, "top_k": 20}
    assert d["sampling_profiles"] == {"reasoning": {"temperature": 0.6,
                                                    "top_p": 0.95}}


def test_clearing_removes_the_key_entirely(tmp_path):
    """A bare `key:` parses to None, same as absent — but "not sent at all" is the
    meaning that matters, so the line goes."""
    p = _write(tmp_path)
    set_yaml_key(p, "sampling", "{ top_p: 0.9 }")
    set_yaml_key(p, "sampling", "")
    text = p.read_text(encoding="utf-8")
    assert "sampling" not in text
    assert "sampling" not in yaml.safe_load(text)


def test_a_new_key_is_appended(tmp_path):
    p = _write(tmp_path)
    set_yaml_key(p, "family", "Qwen")
    assert yaml.safe_load(p.read_text(encoding="utf-8"))["family"] == "Qwen"
