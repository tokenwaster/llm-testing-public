The workspace holds a small utilities module `collkit.py` and its test suite in
`tests/test_collkit.py`. Run the tests: 7 pass, 3 fail.

Your job: fix the bugs in `collkit.py` so all 10 tests pass.

Rules:
- Do NOT modify anything under `tests/` — the grading suite is an identical
  copy, so test edits accomplish nothing.
- The passing tests are load-bearing: a fix that breaks a currently-passing
  test costs you exactly what it gains.
- The three failures are genuine bugs with small, surgical fixes. Read the
  failing assertions carefully — each states precisely what correct behavior is
  (order-preserving de-duplication, partition returning matches first, and
  sliding windows that include the final window).
