"""Regression tests for answer-lane scoring.

Run: .venv/Scripts/python.exe -m pytest tests/ -q

Seeded by the Cohere north-mini-code incident: the model emitted correct
answers with a trailing <|END_OF_TURN_TOKEN|> control token, which defeated
both the numeric and exact matchers and silently zeroed 15 correct answers
(dropping its suite score 0.66 -> 0.28). These tests lock in the fix (strip
control tokens before matching) and the FORMAT-MISS guard that surfaces any
FUTURE extraction/format artifact instead of averaging it in as a 0.
"""
from harness import scoring


class _Task:
    """Minimal stand-in for harness.tasks.Task (score_answer only reads .scoring)."""
    def __init__(self, answer, match="exact", tolerance=None):
        self.scoring = {"answer": answer, "match": match}
        if tolerance is not None:
            self.scoring["tolerance"] = tolerance



def test_extract_strips_cohere_end_of_turn():
    assert scoring.extract_answer("ANSWER: 84041<|END_OF_TURN_TOKEN|>") == "84041"


def test_extract_strips_common_token_families():
    for raw, want in [
        ("ANSWER: 42<|endoftext|>", "42"),
        ("ANSWER: 42<|eot_id|>", "42"),
        ("ANSWER: 42</s>", "42"),
        ("ANSWER: 42<|im_end|>", "42"),
    ]:
        assert scoring.extract_answer(raw) == want, raw



def test_numeric_answer_with_token_scores_one():
    rec = scoring.score_answer(_Task("84041", "numeric"),
                               "ANSWER: 84041<|END_OF_TURN_TOKEN|>")
    assert rec["score"] == 1.0


def test_fraction_answer_with_token_scores_one():
    rec = scoring.score_answer(_Task("61.6667", "numeric", tolerance=0.02),
                               "ANSWER: 185/3<|END_OF_TURN_TOKEN|>")
    assert rec["score"] == 1.0


def test_exact_answer_with_token_and_case_scores_one():
    rec = scoring.score_answer(_Task("tea", "exact"),
                               "ANSWER: TEA<|END_OF_TURN_TOKEN|>")
    assert rec["score"] == 1.0



def test_format_miss_flags_unknown_token_family():
    rec = scoring.score_answer(_Task("42", "numeric"),
                               "ANSWER: 42<<WEIRD_NEW_EOS>>")
    assert rec["score"] == 0.0
    assert "FORMAT-MISS" in rec["summary"]


def test_format_miss_ignores_expected_value_in_reasoning():
    rec = scoring.score_answer(_Task("253", "numeric"),
                               "I first computed 253, then corrected.\nANSWER: 254")
    assert rec["score"] == 0.0
    assert "FORMAT-MISS" not in rec["summary"]


def test_clean_wrong_answer_not_flagged():
    rec = scoring.score_answer(_Task("100", "numeric"), "ANSWER: 7")
    assert rec["score"] == 0.0
    assert "FORMAT-MISS" not in rec["summary"]


def test_numeric_answer_with_a_natural_unit_is_accepted():
    for reply in ("ANSWER: 240 minutes", "ANSWER: 240 min", "ANSWER: ≈ 240 s"):
        rec = scoring.score_answer(_Task("240", "numeric"), reply)
        assert rec["score"] == 1.0, reply


def test_numeric_wrong_value_with_unit_still_zero():
    rec = scoring.score_answer(_Task("240", "numeric"), "ANSWER: 300 minutes")
    assert rec["score"] == 0.0
