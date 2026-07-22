# v0.4 dataset — provenance & corrections

The v0.4 dataset is a **frozen archive** (archived under `major.minor` key `0.4`).
Archives are historical snapshots and are not rewritten for methodology changes —
v0.4 was scored under v0.4's methodology, and that is what it records. The one
exception is a **scoring bug** (not a methodology change), documented below.

## 2026-07-15 — control-token re-score of coherelabs.north-mini-code-1.0

**What:** 13 answer-lane results for `coherelabs.north-mini-code-1.0` were
re-scored from `0.0` to `1.0`. Its v0.4 suite mean rose **0.339 → 0.758**
(rank ~22 → 20).

**Why it's a bug fix, not a rewrite of history:** north emitted the *correct*
answer with a trailing control token (`<|END_OF_TURN_TOKEN|>`) on the ANSWER
line. The v0.4-era `extract_answer` did not strip control tokens, so it failed
to parse 13 correct answers and scored them 0. v0.5.7 fixed `extract_answer`
(the fix is task-agnostic). Re-parsing the **saved, unchanged** model outputs
with the corrected scorer is deterministic — the same operation `harness
rescore` runs on the live set. The task definitions were not touched.

**Isolation:** north is the only model affected — it is the sole control-token
emitter, confirmed by the v0.5.7 suite scan and re-confirmed here (the
correction tool aborts if any other model's score would change). 581 v0.4
answer-lane results were scanned; only these 13 changed.

**Reproduce:** `python tools/correct_v04_north.py` (dry run) / `--apply`.

The corrected `score.json` files carry `(rescored: control-token fix, v0.5.7)`
in their summary.

## Not corrected (methodology, left frozen — read with the caveat)

v0.4 predates the **no-op-floor fixes** (v0.5.5–0.5.6) and the **timing-budget
calibration** (v0.5.9). On the v0.4 agentic tasks a no-op submission could floor
at a non-zero score (e.g. `ag-001` 0.75, `ag-003` 0.43), and timing-sensitive
tasks could be scored under CPU contention. These were *task/checker redesigns*,
so they cannot be retro-applied to v0.4 workspaces without pretending v0.4 used
methods it didn't. Weak-model scores on v0.4 agentic/timing tasks can therefore
be **over-credited**. See CHANGELOG for v0.5.5, v0.5.6, v0.5.9.
