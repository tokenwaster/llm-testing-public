"""0.7.11 scoring fixes: the tally reads pytest's final line, the pytest lane
ignores model-written conftest/ini files, code fences are matched regardless
of tag case, ANSWER: is case- and markdown-tolerant, and two more terminator
families are stripped."""
import types

from harness import scoring


class _Task:
    def __init__(self, answer, match="exact"):
        self.scoring = {"answer": answer, "match": match}


def _run(out, tmp_path, monkeypatch):
    class _P:
        timed_out = False
        returncode = 1
        stdout = out
        stderr = ""
    monkeypatch.setattr(scoring, "run_capped", lambda *a, **k: _P())
    chk = tmp_path / "checker.py"
    chk.write_text("def test_x():\n    assert True\n", encoding="utf-8")
    task = types.SimpleNamespace(checker=chk, checker_timeout_s=60, scoring={})
    return scoring.run_pytest_checker(task, tmp_path)


def test_tally_ignores_a_test_count_quoted_in_an_assertion_message(
        tmp_path, monkeypatch):
    out = ("F.\n"
           "=== short test summary info ===\n"
           "FAILED test_checker.py::test_q4 - AssertionError: got '100 passed'\n"
           "1 failed, 1 passed in 0.04s\n")
    r = _run(out, tmp_path, monkeypatch)
    assert r["summary"].startswith("1/2 tests passed"), r["summary"]
    assert r["score"] == 0.5


def test_tally_reads_the_banner_form_too(tmp_path, monkeypatch):
    out = "....\n========= 4 passed in 0.10s =========\n"
    assert _run(out, tmp_path, monkeypatch)["score"] == 1.0


def test_tally_counts_errors_with_failures(tmp_path, monkeypatch):
    out = "..EF\n2 passed, 1 failed, 1 error in 0.2s\n"
    r = _run(out, tmp_path, monkeypatch)
    assert r["summary"].startswith("2/4 tests passed")


def test_no_summary_line_means_no_tests_ran(tmp_path, monkeypatch):
    out = "10 passed\nsomething printed by the submission itself\n"
    r = _run(out, tmp_path, monkeypatch)
    assert r["score"] == 0.0 and "no tests ran" in r["summary"]


def test_the_pytest_lane_is_isolated_from_the_workspace(tmp_path, monkeypatch):
    seen = {}

    class _P:
        timed_out = False
        returncode = 0
        stdout = "1 passed in 0.01s\n"
        stderr = ""

    def fake(cmd, timeout, **kw):
        seen["cmd"] = cmd
        seen["env"] = kw["env"]
        seen["ini_present"] = (tmp_path / scoring.HARNESS_INI).exists()
        return _P()
    monkeypatch.setattr(scoring, "run_capped", fake)
    chk = tmp_path / "checker.py"
    chk.write_text("def test_x():\n    assert True\n", encoding="utf-8")
    task = types.SimpleNamespace(checker=chk, checker_timeout_s=60, scoring={})
    scoring.run_pytest_checker(task, tmp_path)
    cmd = seen["cmd"]
    assert "--noconftest" in cmd
    assert "-I" in cmd, "cwd must not shadow pytest itself"
    assert cmd[cmd.index("-c") + 1] == scoring.HARNESS_INI
    assert seen["ini_present"], "the empty ini must exist while pytest runs"
    assert not (tmp_path / scoring.HARNESS_INI).exists(), "and be gone after"
    assert seen["env"].get("PYTEST_ADDOPTS") == ""


def test_a_model_conftest_cannot_flip_outcomes(tmp_path):
    """End-to-end: the hookwrapper that turns every failure into a pass."""
    (tmp_path / "conftest.py").write_text(
        "import pytest\n"
        "@pytest.hookimpl(hookwrapper=True)\n"
        "def pytest_runtest_makereport(item, call):\n"
        "    out = yield\n"
        "    rep = out.get_result()\n"
        "    if rep.when == 'call':\n"
        "        rep.outcome = 'passed'\n", encoding="utf-8")
    (tmp_path / "pytest.ini").write_text("[pytest]\naddopts = -p no:python\n",
                                         encoding="utf-8")
    chk = tmp_path / "checker_src.py"
    chk.write_text("def test_fails():\n    assert False\n"
                   "def test_ok():\n    assert True\n", encoding="utf-8")
    task = types.SimpleNamespace(checker=chk, checker_timeout_s=60, scoring={})
    r = scoring.run_pytest_checker(task, tmp_path)
    assert r["summary"].startswith("1/2 tests passed"), r


def test_code_fence_tag_is_case_insensitive_and_skips_trailing_examples():
    text = ("```Python\ndef f():\n    return 1\n```\n"
            "Example:\n```\n>>> f()\n1\n```\n")
    assert scoring.extract_code_block(text) == "def f():\n    return 1\n"
    assert scoring.extract_code_block("```python3\nimport os\n```") == \
        "import os\n"
    assert scoring.extract_code_block("no fence") is None


def test_answer_line_tolerates_case_and_markdown():
    for raw in ("Answer: 253", "**ANSWER:** 253", "ANSWER: **253**",
                "answer: `253`", "  ANSWER : 253  "):
        assert scoring.extract_answer(raw) == "253", raw
    assert scoring.score_answer(_Task("253", "numeric"), "Answer: 253")["score"] == 1.0


def test_gemma_and_deepseek_terminators_are_stripped():
    assert scoring.extract_answer("ANSWER: 253<end_of_turn>") == "253"
    assert scoring.extract_answer("ANSWER: 253<｜end▁of▁sentence｜>") == "253"
    assert scoring.score_answer(_Task("253", "numeric"),
                                "ANSWER: 253<end_of_turn>")["score"] == 1.0
