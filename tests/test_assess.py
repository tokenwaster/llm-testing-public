"""Attribution must not blame us for the model's failures, or vice versa.

Two real misfires, both caught on live v0.6 data:

  * rs-010-ants-rod fired as `suspect-answer-key [harness]` because two strong
    models both answered '40' - the REGISTERED TRAP. Six other models answered
    it correctly, so the key was provably fine. The verdict is attributed to us,
    so falling for a trap was excluded from the model's attributed score:
    claude-cli-opus-4-8 read 0.947 raw but 0.970 attributed.
  * adapters raise kind="rumination_spiral" for thinking with no output; assess
    only matched "runaway", so it fell through to checker-fail - "code ran but
    failed the checker's tests" for a model that emitted an empty workspace.
"""

from types import SimpleNamespace

from harness import assess


def _tdef(tid="rs-010-ants-rod"):
    return SimpleNamespace(id=tid, category="reasoning", scoring_type="answer")


def _res(got, score=0.0):
    return {"status": "ok", "attempts": [{"stop_reason": "stop"}],
            "score": {"status": "scored", "score": score,
                      "summary": f"expected '61.6667', got '{got}' (numeric)"}}


def _cfg(**over):
    c = dict(assess.DEFAULTS)
    c["traps"] = {"rs-010-ants-rod": ["40"]}
    c.update(over)
    return c



def test_a_registered_trap_is_the_models_fault_not_ours():
    cfg = _cfg()
    suspect = {"rs-010-ants-rod": {"answer": "40", "models": ["a", "b"],
                                   "strength": 0.92}}
    cls = assess.classify(_res("40"), _tdef(), cfg, suspect)
    assert cls["category"] == "fell-for-trap", cls
    assert cls["attribution"] == "model", \
        "a trap answer must never be attributed to the harness - that hands the " \
        "model a free pass on the exact failure the task exists to catch"


def test_suspect_key_stands_down_when_anyone_solved_it():
    """Six models answering correctly proves the key works."""
    cfg = _cfg()
    agg = {f"weak{i}": _res("40") for i in range(3)}
    agg["strong"] = _res("61.6667", score=1.0)
    td = {"rs-010-ants-rod": {"agg": agg}}
    out = assess.suspect_answers(td, {"rs-010-ants-rod": _tdef()}, cfg)
    assert out == {}, f"key is provably answerable; nothing suspect: {out}"


def test_suspect_key_still_fires_when_nobody_solved_it():
    """The heuristic must still earn its keep: an unsolved task where strong
    models converge on one answer is exactly what it is for."""
    cfg = _cfg(suspect_key_min_avg=0.0)
    cfg["traps"] = {}
    td = {"rs-999-x": {"agg": {f"m{i}": _res("40") for i in range(3)}}}
    out = assess.suspect_answers(td, {"rs-999-x": _tdef("rs-999-x")}, cfg)
    assert "rs-999-x" in out, "nobody solved it and 3 models agree — flag it"


def test_a_trap_answer_is_never_a_suspect_key():
    cfg = _cfg(suspect_key_min_avg=0.0)
    td = {"rs-010-ants-rod": {"agg": {f"m{i}": _res("40") for i in range(3)}}}
    out = assess.suspect_answers(td, {"rs-010-ants-rod": _tdef()}, cfg)
    assert out == {}, "'40' is the registered trap, not evidence of a bad key"



def test_rumination_spiral_is_recognised():
    res = {"status": "error",
           "attempts": [{"error_kind": "rumination_spiral", "tokens_out": None,
                         "error": "rumination spiral: 300s of thinking with no "
                                  "output at all"}],
           "score": {"status": "scored", "score": 0.0,
                     "summary": "run failed (all attempts errored)"}}
    tdef = SimpleNamespace(id="web-012-coin", category="one-shot-apps",
                           scoring_type="webapp")
    cls = assess.classify(res, tdef, _cfg())
    assert cls["category"] == "rumination-spiral", \
        f"an empty workspace is not 'code ran but failed the tests': {cls}"
    assert cls["attribution"] == "model"


def test_runaway_still_recognised():
    res = {"status": "error",
           "attempts": [{"error_kind": "runaway", "tokens_out": 32768,
                         "error": "degenerate repetition loop"}],
           "score": {"status": "scored", "score": 0.0, "summary": "x"}}
    tdef = SimpleNamespace(id="py-005", category="coding-python",
                           scoring_type="pytest")
    assert assess.classify(res, tdef, _cfg())["category"] == "rumination-spiral"
