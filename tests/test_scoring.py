from harness import scoring


class _Task:
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


COLLECT_ERR = """
=================================== ERRORS ====================================
______________________ ERROR collecting test_checker.py _______________________
E     File "solution.py", line 43
E       elif char == '"':
E   IndentationError: expected an indented block after 'else' statement on line 40
=========================== short test summary info ===========================
ERROR test_checker.py
1 error in 0.11s
"""

NO_SUBMISSION = """
=================================== ERRORS ====================================
______________________ ERROR collecting test_checker.py _______________________
E   ModuleNotFoundError: No module named 'solution'
1 error in 0.09s
"""

REAL_FAILURE = """
FAILED test_checker.py::test_whitespace - ValueError: bad char
1 failed, 8 passed in 0.02s
"""


def _summary(out, tmp_path, monkeypatch, cap=None):
    import types

    from harness import scoring

    class _P:
        timed_out = False
        returncode = 1
        stdout = out
        stderr = ""

    monkeypatch.setattr(scoring, "run_capped", lambda *a, **k: _P())
    chk = tmp_path / "checker.py"
    chk.write_text("def test_x():\n    assert True\n", encoding="utf-8")
    task = types.SimpleNamespace(
        checker=chk, checker_timeout_s=60,
        scoring={} if cap is None else {"automated_max": cap})
    return scoring.run_pytest_checker(task, tmp_path)


def test_a_broken_submission_names_the_error_not_a_test_count(tmp_path,
                                                              monkeypatch):
    r = _summary(COLLECT_ERR, tmp_path, monkeypatch)
    assert r["score"] == 0.0
    assert "does not import" in r["summary"]
    assert "IndentationError" in r["summary"]
    assert "0/1 tests passed" not in r["summary"]


def test_a_missing_submission_says_so(tmp_path, monkeypatch):
    r = _summary(NO_SUBMISSION, tmp_path, monkeypatch)
    assert r["score"] == 0.0
    assert "ModuleNotFoundError" in r["summary"]


def test_a_real_test_failure_still_reports_the_count(tmp_path, monkeypatch):
    r = _summary(REAL_FAILURE, tmp_path, monkeypatch)
    assert r["summary"].startswith("8/9 tests passed")
    assert r["score"] == round(8 / 9, 4)


def test_a_capped_task_keeps_its_ceiling_on_a_real_failure(tmp_path, monkeypatch):
    r = _summary(REAL_FAILURE, tmp_path, monkeypatch, cap=0.8)
    assert r["score"] == round((8 / 9) * 0.8, 4)
