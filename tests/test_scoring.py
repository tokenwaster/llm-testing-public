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


def test_a_cell_that_never_reached_the_provider_is_not_a_score():
    from harness.runner import never_reached_provider
    assert never_reached_provider([
        {"error": "connect failed: [Errno 11001] getaddrinfo failed",
         "error_kind": "connect"},
        {"error": "connection forcibly closed", "error_kind": "connect"}]), (
        "no request was ever delivered, so nothing about the model was "
        "measured; scoring that 0 charges a DNS failure to the model")


def test_a_provider_that_answered_badly_still_earns_its_zero():
    from harness.runner import never_reached_provider
    reached = [
        [{"error": "ResourceExhausted: Worker local total request limit "
                   "reached (32/32)", "error_kind": "api"}],
        [{"error": "Provider returned an empty response", "error_kind": "api"}],
        [{"error": "no html code block in response", "error_kind": "runaway",
          "tokens_out": 65536}],
        [{"error": "exceeded the 600s budget", "error_kind": "timeout"}],
        [{"error": "HTTP 400: request exceeds the available context",
          "error_kind": "api"}],
    ]
    for attempts in reached:
        assert not never_reached_provider(attempts), (
            f"{attempts[0]['error'][:40]!r} came back FROM the provider — a "
            f"full endpoint or an empty reply is the product behaving badly, "
            f"which is a real mark against buying the model that way")


def test_one_delivered_attempt_is_enough_to_score_the_cell():
    from harness.runner import never_reached_provider
    assert not never_reached_provider([
        {"error": "stream broke", "error_kind": "connect"},
        {"tokens_out": 500}])
    assert not never_reached_provider([
        {"error": "stream broke", "error_kind": "connect",
         "tokens_out": 120}]), (
        "tokens arrived, so the model did speak; a truncated answer is a "
        "measurement, not a missed connection")
    assert not never_reached_provider([])
    assert not never_reached_provider([{"tokens_out": 900}])


def test_the_runner_writes_no_score_when_nothing_was_reached():
    import inspect

    from harness import runner
    src = inspect.getsource(runner.TaskRunner.run_task)
    i = src.index("never_reached_provider(attempts)")
    seg = src[i:i + 700]
    assert 'unlink(missing_ok=True)' in seg, (
        "an unscored cell must leave no score.json at all; a score.json with "
        "status=unscored would still be a file the next reader has to reason "
        "about")
    assert '"score": None' in seg
    assert "self._score(" in seg.split("else:")[-1], (
        "every other outcome still goes through the normal scoring lane")


def test_endpoint_and_model_failures_are_told_apart():
    from harness.report import attempt_blame
    endpoint = [
        {"error": "HTTP 429: Provider returned error", "error_kind": "rate_limit"},
        {"error": "connect failed: getaddrinfo failed", "error_kind": "connect"},
        {"error": "empty response from the provider", "error_kind": "transport"},
        {"error": "in-body error: Upstream error from Nvidia: "
                  "ResourceExhausted: Worker local total request limit reached "
                  "(33/32)", "error_kind": "api"},
        {"error": "in-body error: Provider returned an empty response",
         "error_kind": "api"},
    ]
    model = [
        {"error": "no ANSWER: line in response", "error_kind": "format"},
        {"error": "no html code block in response", "error_kind": "runaway"},
        {"error": "exceeded the 600s budget", "error_kind": "timeout"},
        {"error": "repetition loop", "error_kind": "repetition_loop"},
        {"error": 'HTTP 400: request (188599 tokens) exceeds the available '
                  'context', "error_kind": "api"},
        {"error": "claude CLI failed: error_max_turns", "error_kind": "api"},
    ]
    for a in endpoint:
        assert attempt_blame(a) == "endpoint", a["error"][:50]
    for a in model:
        assert attempt_blame(a) == "model", a["error"][:50]
    assert attempt_blame({"tokens_out": 100}) == "clean"


def test_an_unrecognised_failure_is_charged_to_the_model():
    from harness.report import attempt_blame
    assert attempt_blame({"error": "something nobody has seen before",
                          "error_kind": "api"}) == "model", (
        "the wording list is best-effort; an unknown phrase must never invent "
        "an excuse for a model, so the conservative default is to blame it")


def test_availability_counts_attempts_not_cells():
    from harness.report import availability
    rs = [
        {"model": "m", "task": "t1", "attempts": [
            {"error": "HTTP 429", "error_kind": "rate_limit"},
            {"tokens_out": 50}]},
        {"model": "m", "task": "t2", "attempts": [{"tokens_out": 80}]},
    ]
    a = availability(rs)
    assert a["attempts"] == 3 and a["endpoint_failures"] == 1
    assert a["availability"] == round(2 / 3, 4)
    assert a["cells"] == ["t1"] and a["n_cells"] == 1
    assert availability([])["availability"] is None


def test_a_throttled_model_still_loses_its_score():
    from harness.report import availability
    rs = [{"model": "m", "task": "t", "score": {"status": "scored",
                                                "score": 0.0},
           "attempts": [{"error": "HTTP 429", "error_kind": "rate_limit"}]}]
    a = availability(rs)
    assert a["endpoint_failures"] == 1
    assert "score" not in a, (
        "availability reports blame, it does not adjust or forgive the score — "
        "a model you cannot get an answer out of is a worse model to buy")


def test_the_uptime_column_and_row_are_on_the_pages():
    from harness import config
    src = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")
    assert ">Uptime</th>" in src
    assert "{{ r.avail }}" in src and "{{ r.avail_why }}" in src
    assert "def _availability_row" in src
    assert 'id="availability"' in src, "the split needs an info-page anchor"
    assert 'href="info.html#availability"' in src


def test_a_100_percent_model_says_so_plainly():
    from harness.report import _availability_row
    row = _availability_row({"avail": {"attempts": 116, "endpoint_failures": 0,
                                       "kinds": {}, "cells": [], "n_cells": 0},
                             "avail_pct": 100.0})
    assert "100%" in row["v"] and "116" in row["v"]
    assert _availability_row({"avail": {"attempts": 0}}) is None


def test_the_shared_answer_verifier_does_not_bluff_on_a_regex_task():
    from harness import config
    src = (config.ROOT / "tasks-refs" / "_verify.py").read_text(
        encoding="utf-8")
    i = src.index('if mt == "regex":')
    seg = src[i:i + 700]
    assert "no correct response can be derived" in seg, (
        "it used to build the 'correct' case by pasting the answer field into "
        "an ANSWER line, which for a regex key is a pattern — it reported a "
        "sound task as FAILED")
    assert "verify.py" in seg


def _ledger():
    import sys
    from harness import config
    p = config.ROOT / "tasks-refs" / "rs-014-ledger-amend-chain"
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
    import generate
    return generate


def test_the_ledger_key_survives_a_second_independent_resolver():
    import sys
    from harness import config
    g = _ledger()
    p = str(config.ROOT / "tasks-refs" / "rs-014-ledger-amend-chain")
    if p not in sys.path:
        sys.path.insert(0, p)
    import verify as v
    for seed in (14, 46, 78, 110):
        d = g.build(seed)
        assert v.from_text(g.render(d), d["target"]) == d["answer"], (
            f"seed {seed}: re-reading the rendered log disagrees with the "
            f"generator, so the key rests on one implementation — the mistake "
            f"that shipped two dead tasks before this one")


def test_every_shortcut_lands_on_a_different_wrong_number():
    g = _ledger()
    for seed in (14, 46, 78, 110, 142):
        d = g.build(seed)
        vals = d["traps"]
        assert d["answer"] not in vals.values(), (
            f"seed {seed}: a shortcut reaches the right answer, so the task "
            f"rewards not reading carefully")
        assert len(set(vals.values())) >= 3, f"seed {seed}: {vals}"


def test_the_ledger_answer_is_not_guessable():
    g = _ledger()
    keys = [g.build(s)["answer"] for s in range(1, 31)]
    assert len(set(keys)) == len(keys), "a key repeats across seeds"
    assert max(abs(k) for k in keys) > 500, "the range is too narrow to matter"


def test_missing_one_entry_changes_the_total():
    g = _ledger()
    d = g.build(14)
    mine = {op["tid"] for op in d["lines"]
            if op["op"] == "post" and op["account"] == d["target"]}
    counting = []
    for tid in mine:
        gate = [op["op"] for op in d["lines"]
                if op["tid"] == tid and op["op"] in ("void", "restore")]
        if not (gate and gate[-1] == "void"):
            counting.append(tid)
    assert len(counting) >= 10, (
        f"only {len(counting)} entries count towards the answer; the "
        f"mechanism this task is built on is exhaustive aggregation, which "
        f"needs enough items that missing one is likely")
    for tid in counting[:5]:
        without = [op for op in d["lines"] if op["tid"] != tid]
        assert g.resolve(without, d["target"]) != d["answer"], (
            f"dropping {tid} leaves the total unchanged, so it is not load "
            f"bearing")
