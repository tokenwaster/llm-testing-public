# Changelog

All notable changes to the test suite and the harness.

**Versioning policy.** `SUITE_VERSION` versions the *test dataset*, not the code:

- **Minor/major bump** (`0.4` → `0.5`) — the tests or the methodology changed.
  The old data is archived first (`harness archive --as 0.4`) so live reports
  always show exactly one coherent dataset.
- **Patch bump** (`0.5.6` → `0.5.7`) — scoring fixes and presentation changes
  *within* a dataset. Patches never archive: the archive key is `major.minor`,
  so every `0.5.x` run aggregates into the same "0.5" dataset.
- **No bump** — run-engine, server, and UI changes that don't affect what is
  tested or how it is scored.

Scores are aggregated as the **mean of every scored run per model·task**, so
re-running a model fleshes its number out rather than replacing it; unscored
runs (crash / spiral / DNF) stay out of the mean.

**Changelog layout.** Only the top `## Unreleased` section holds pending work;
its entries are `###` subsections. When a version is cut, those subsections move
under the new `## x.y.z` header. So every `###` below a version number belongs to
that version — there is never an `## Unreleased` stranded between two releases.

---

## Unreleased

## 0.6.15 — confidence bands + public-site fixes

**Headline confidence (G2).** Every model's score now carries its 95% band
(±1.96·SE across the task set), shown on the overview matrix, the leaderboard
podium, and the model-page raw-score tile. On the matrix, a model is marked ≈
when its band overlaps the leader's — i.e. it is not statistically
distinguishable from #1 on this suite. On the current data that flags the top 8
as one tied cohort, the honest reading of the frontier compression the
discriminate page already reports. Computed from scores already on hand — no new
runs. Presentation only, but bundled here under a patch tag.

**Cost is one pass, by design (confirmed, not changed).** Cost and total time
aggregate as the MEAN per model·task (`cost_usd` is in `_aggregate`'s
`_MEAN_FIELDS`), summed across tasks — i.e. the cost of one full pass, not
inflated by how many times a model was re-tested. Uniform across the tile,
podium, and leaderboard.

**Public-site fixes** shipped this cycle: model pages link out to Hugging
Face / OpenRouter without needing the private model yaml; the `/data` browser
resolves archived-dataset runs (was 404ing ~2600 links); the info-page catalog
and run-report grid no longer emit dead task links; the public build defaults to
port 9001; the rendered `reports/` site now ships in the public repo. A stale
call convention that crashed the operator `/backend` endpoint was fixed.

## 0.6.14 — price refresh + free-tier honesty

`harness prices` re-reads gateway list prices into the model yamls and stamps
`pricing_asof:`, so a frozen snapshot stops quietly turning into a lie. Dry-run
by default, `--apply` writes. LOCAL models are excluded: they are served over the
same openai-compatible provider and their ids often match a catalog entry
verbatim (`qwen/qwen3-32b`), but they cost measured electricity, not the
gateway's rate — the first dry run caught exactly that and would have stamped
cloud prices on six local models.

The first real refresh found the drift this exists for: **four free tiers had
already ended** (gemini-3.5-flash 0 -> 1.5/9.0, kimi-k3 0 -> 3.0/15.0,
kimi-k2.7-code, gpt-oss-120b) and glm-5.2 had nearly doubled (0.42/1.32 ->
0.819/2.574).

It never rewrites history: `cost_usd` is computed per result at RUN time, so
refreshed prices apply to future runs and to anything that displays list price —
already-recorded costs stay as they were (and for gateway models those were the
actual billed amount anyway).

Task fit also stopped letting a promotional `:free` price win "cheapest that
works" — free-tier is derived from OpenRouter's `:free` id, promos are shown
apart as "free now" with a ⏳ label, and the pick now names durable costs (local
electricity or a genuinely paid API).

## 0.6.13 — five public-capability lanes

The suite was developer-heavy (code, logic puzzles, long-context, one-shot apps)
and blind to what the general public actually uses LLMs for. Added five new
categories, each with a **discriminator** (broad separator) and a **frontier**
(top separator) task — 10 tasks, 42 → 52:

- **instruction-following** (if-001 exact-format, if-002 stacked self-referential
  constraints) — does the model obey precise output rules.
- **hallucination** / abstention (hl-001, hl-002) — grounded-passage QA where some
  questions are unanswerable-from-text; correct = abstain, not fabricate.
- **math** (math-001 money multi-step, math-002 multi-phase pipe rates) — practical
  numeric word problems, distinct from the reasoning lane's logic puzzles.
- **extraction** (ext-001 fields→JSON, ext-002 nested/normalized with null-not-guess).
- **tool-use** (tool-001 select+fill, tool-002 refuse-to-fabricate-missing-args) —
  **prompt-based JSON** call generation, so the Claude CLI flagship and non-tool
  locals all participate (no native tools API required).

New **`response` scoring lane**: the model's raw reply is saved as `response.txt`
and a `checker.py` runs against it (same pytest machinery as the code lane, no
forced format instruction). Math uses the existing numeric answer lane. All 10
reference-verified — known-good → 1.0, empty → 0.0 — via
`tasks-refs/_verify_response.py` and `_verify.py`.

Added **mid-baseline as a patch** (no archive, same 0.6 bucket): existing models
show the new tasks as "not run" until topped up. Select them with the **✦ New**
quick-select on /run or `harness run --tasks new` (`config.NEW_TASKS`). Engine
touch-ups: `rescore.py` handles the response lane; the /info lane guide lists it.
tests/test_new_lanes.py; the hardened "every lane represented" invariant now
scopes to established lanes (new lanes start unhardened by design).

## 0.6.12 — coalesce fitting buckets into one load

Per-context bucketing reloaded a model once per distinct context even when every
bucket fit VRAM — gemma-4-e4b (5.3GB, needs only 14.6GB even at its 205k context)
was doing 5 loads for nothing. load_plan() now coalesces all buckets that fit
('--gpu max') into a SINGLE load at the largest fitting context, and keeps only
genuine overflow buckets separate (each on '--gpu auto' at its own context, so an
oversized task isn't loaded at a needlessly larger window). Result: e4b and
gemma-4-12b load ONCE (all 42 tasks); gemma-4-31b loads 3x (40 tasks --gpu max @
82k, then the two overflow tasks on auto) instead of 5. Score-neutral (a task run
at a larger-but-fitting window produces the same output). tests/test_context_load.py.
Patch, no archive.


## 0.6.11 — 'auto' means omit the flag (fix 0.6.10)

0.6.10 passed `--gpu auto` for overflow buckets, but lms only accepts `off`,
`max`, or a 0..1 number — it rejects `auto` ("not a number"). So the overflow
loads FAILED and fell back to a JIT load at the model's native context, i.e.
straight back to the spill-freeze. Auto is lms's default when `--gpu` is omitted,
so load_model now omits the flag for "auto" (only passes `--gpu` for "max"/"off"/
ratio). tests/test_context_load.py covers it. Patch, no archive.


## 0.6.10 — VRAM-aware GPU offload (fix 0.6.9's spill-freeze)

0.6.9 forced `--gpu max` on every local load. Great when the model fits (8 -> 57
tok/s), catastrophic when a context is too big: `--gpu max` puts ALL layers on
the GPU regardless of fit, so an oversized bucket (gemma-4-31b's 128k task, ~38GB
working set on a 32GB card) spilled into Windows shared system RAM at ~0.03 tok/s,
the 300s warm-up timed out, the model was skipped, AND it was left resident —
pinning 32GB of VRAM and freezing the whole desktop.

Now the offload ratio is decided per bucket from the GGUF footprint + the card's
VRAM (`_bucket_offload`):
- fits VRAM (with 10% headroom) -> `--gpu max` (full GPU, fast).
- would overflow -> `--gpu auto` (LM Studio parks the excess on the CPU; the task
  runs slow ~5 tok/s but COMPLETES, VRAM keeps headroom, no freeze). Verified:
  gemma-4-31b @ 205k with auto = 2.1GB VRAM used / 30GB free, 4.8 tok/s, vs
  `--gpu max` 32.1GB pinned / 0.03 tok/s / hang.
- can't measure (no nvidia-smi or GGUF header) -> `auto` (never risk a spill).

And a local model is now UNLOADED on every exit path (run_model's finally: done,
warm-up fail, rate limit, crash), so a finished or aborted load never sits pinning
VRAM. That was the second half of the freeze.

tests/test_context_load.py covers the max/auto/unknown decision. No archive
(patch). 

## 0.6.9 — local models actually use the GPU

### Full GPU offload + batch-sized context

Local models crawled at ~8 tok/s on a 32GB card with VRAM to spare. Two causes,
found by measuring GPU utilisation during generation (17%, not offload-looking),
not by theory:

1. **`lms load` defaulted to "auto" GPU offload**, which left transformer layers
   on the CPU even with 11GB VRAM free — GPU sat at 17%, one CPU core pinned.
   Forcing **`--gpu max`** puts every fitting layer on the GPU: gemma-4-31b went
   **8 → 57 tok/s (17% → 82% GPU)**, verified through the harness's own loader.
2. **The run loaded ONE window sized to the largest task.** One 128k-context task
   (ctx-008) forced a ~205k window (~37GB > card), so even `--gpu max` couldn't
   fit it and the *whole run* spilled to shared system RAM. Now
   `context_buckets()` groups tasks by the window they need and loads ascending:
   the ~40 short-context tasks load in a ~49k window (~28GB, fully on GPU, fast)
   and only the genuine long-context task loads oversized and stays slow.

Both were needed: `--gpu max` alone still crawls if the window doesn't fit (a
single load at 205k timed out); bucketing alone doesn't help if auto-offload
leaves layers on the CPU.

Scores are unchanged (same prompt/budget/weights → same output); only speed
moves. So local-model speed metrics step up on this date and are **not comparable
to earlier runs** — the /info page says so, and each run stamps its load plan
(`load_strategy`, `context_groups`) into `model_meta.json`. No `SUITE_VERSION`
bump: run-engine behaviour, nothing tested or scored changed. Removed the now
dead `needed_context`. Tests: `tests/test_context_load.py`.

## 0.6.8 — test it again and the number gets better

**Patch bump — the aggregation basis changed, and no existing number moved.**
Proven, not asserted: rendering the whole site with the previous code and diffing
gives **630 of 630 score chips identical**. Every model·task in the dataset has
been measured exactly once, and the mean of one value is that value. The change
only takes effect the first time something is actually re-tested — so v0.6 stays
live and keeps its baseline rather than being archived behind a new minor.

### What changed

Aggregation was **latest result per model·task**. It is now **the mean of every
run of that model·task in the dataset**. Testing something again fleshes the
number out instead of replacing it.

Latest-wins had never once had to disambiguate anything: not in live v0.6 (7
runs, 630 pairs) and not in the v0.5 archive (22 runs, 1,365 pairs). Zero pairs
were ever measured twice. The rule was untested and, for repeat trials, wrong —
simulating `--repeat 3` with trials of 1.0/0.5/0.0 reported a headline of
**0.0**, the last trial, worst purely by run order, while the σ column reported
±0.408 for three samples the headline had thrown away.

### The rules

- **Mean of every scored run.** Order cannot matter; a 4th run moves it again.
- **Unscored runs stay out of the mean** (crash, spiral, DNF) — `_summarize`
  counts only `status=="scored"` toward a model's average, so a failed trial must
  not silently become a 0 here when it isn't one there. The run still counts as
  having happened (`n_runs`), and history keeps everything.
- **Cost, wall and tokens mean rather than accumulate.** They describe ONE pass,
  so re-testing must not make a model look slower or more expensive.
- **A rescore still supersedes** — it re-grades the same run in place rather
  than adding one. A genuinely botched run is deleted on /manage
  (`/api/delete-result`, run·model·task granularity) rather than averaged in.

### Honesty in the UI

A mean of several runs must never render as a lone measurement: a score built
from more than one run now carries `±σ` and an `×N` badge naming the runs, and
the files link says it opens the newest of N. Every heading that claimed "latest
result per task" now says what it does. `info["latest"]` is renamed
`info["agg"]` across report.py and assess.py — a key called "latest" holding a
mean is exactly the kind of lie that bites later.

/info documents the new basis, including that a rescore supersedes but a re-run
averages.

Tests: `tests/test_aggregate_repeats.py` (16) covers the mean, order-independence,
the 4th-run case, unscored exclusion, all-unscored, and the cost/wall means.

### σ is now per task, and it names the culprit (no bump — presentation)

The consistency column was the spread of a model's whole-**suite** average
between runs. It answered nothing. It read `—` for **all 15 models**, because
each has exactly one run — and the moment it *did* have data it would have been
wrong: a partial re-run of 5 hard tasks gets compared against a 42-task pass and
the gap reported as "inconsistency". Spread only means anything against the
**same** task.

- **`σ per task`** on the overview — the mean of the per-task σ over the tasks
  actually re-run, with a sub-label saying how many were (`2 tasks re-run`), and
  a tooltip listing the worst offenders. When nothing has been repeated it says
  so and names the command that would fix that, instead of a dead dash.
- **`Least stable`** column — the single task whose score moved most. This is
  the question the old column couldn't answer.
- **A σ column on each model page's per-task table**, which is where "which task
  is flaky" actually gets read.

Three states that used to look identical are now distinct: run once (`—`), run
3× and never moved (`±0.000`), run 3× and wobbled (`±0.471 ×3`).

Verified by forcing repeats against live data — grok-4.5 re-run on
rs-011 (0.0/1.0) and web-007-life (1.0/1.0) renders `±0.236 · 2 tasks re-run`
with `Least stable: rs-011-gear-axle-train ±0.471`, while its steady task shows
`±0.000 ×3`. Tests: `tests/test_consistency.py` (9). 160 passing.

Also quoted the model page's `/data` links (they interpolated the raw model name
into a URL).

## 0.6.7 — the fan that wouldn't stop, again

**Patch bump — process hygiene in the grading lanes.** No test changed its
verdict: `ag-002`/`ag-006` were re-scored against real saved workspaces and
returned exactly what they returned before (glm-5.2 1.0 → 1.0, qwen3.5-9b
0.0 → 0.0). `ag-002` and `ag-006` do get new `content_hash` values, since their
checker source changed; that is provenance, not invalidation — no recorded score
moves, and `task_hash` has never gated aggregation.

### The bug

After a finished run the fans stayed at full. A `python.exe` was burning
**19,202s of CPU — 5.3 hours** on 11 MB of RAM, its parent long gone. It was
computing:

```
assert perf.fib(300) == 222232244629420445529739893461909967206666939096499764990979600
```

qwen3.5-9b never memoised `fib`, so its naive exponential recursion was never
going to finish. Its checker had timed out, scored it 0.0, and moved on **45
seconds in** — the process just never died with it.

### Why the timeout didn't kill it

`subprocess.run(timeout=)` reaps only the **direct** child, and on Windows a
venv's `python.exe` is a launcher shim. So the deadline killed the shim and left
the real interpreter running. `taskkill /T` walks the *live* parent→child
snapshot, which means it has to run **while the top process is still alive**;
once the parent exits, the orphans keep a stale PPID and `/T` can no longer find
them. This is the exact trap already documented for `claude -p`'s worker fork
(`adapters._terminate_tree`) — the fix had simply never been applied to the
grading side.

The real culprit was one layer up from the checkers: **`scoring.run_pytest_checker`**,
which every pytest and webapp task in the suite goes through. When *its* deadline
fired it orphaned the whole subtree beneath it — pytest itself, ag-006's timed
workloads, and Playwright's node+Chromium (the same leak that once left 11
Chromiums running). Fixing only the checkers was not enough: the outer kill
pre-empted the inner one, so the careful tree-kill never got to run.

### This corrupts scores, not just the fans

ag-006 and the webapp lane calibrate their budgets against the CPU **as it is
right now**. An orphan spinning a core is exactly the contention that once scored
a correct 0.3s submission 0.0. A leak here silently damages the tasks that run
*later*.

### The fix

- `util.terminate_tree` — hoisted out of `adapters.py` (the checker lane should
  not import the model adapters to get a kill), same behaviour, now shared.
- `util.run_capped` — `subprocess.run(timeout=)` with the tree reaped: Popen +
  communicate + `terminate_tree`, returning `timed_out` so a killed process is
  distinguishable from one that merely exited non-zero.
- Applied at every deadline that fires on a process which spawns others:
  `scoring.run_pytest_checker` (all pytest + webapp grading), `tools.run_script`
  (**model-authored** code — the likeliest thing here to loop forever),
  `lmstudio` load/unload (`lms` is node behind a shim), and defensively inside
  the `ag-002`/`ag-006` checkers, which are self-contained by design and cannot
  import the harness.
- `nvidia-smi` (`runner`, `telemetry`) deliberately left alone: a leaf binary
  that forks nothing.

### Tests

`tests/test_checker_tree_kill.py` — spawns a parent whose grandchild never
exits, and fails if the grandchild survives the deadline. Also asserts the
scoring lane still routes through `run_capped`, so this cannot silently regress.
122 passing.

## 0.6.6 — the coin's last 0.2 belongs to a human

**Patch bump — scoring model for `web-012-coin`.** No task prompt changed; no
archive. `harness rescore --tasks web-012-coin` applied.

The render lane keeps proving it can verify **mechanics** and cannot judge
**craft**: gpt-5.6-sol passed every mechanical check with **mirrored lettering**,
because relief, specular and rotation are all perfect when the words read
backwards. Four separate pixel heuristics have each been fooled by a different
model's decoration. So stop pretending the machine can award the whole thing.

**New split.** `meta.yaml` declares `automated_max: 0.8` (honoured generically by
`scoring.run_pytest_checker`, so any task may cap what the machine alone can
give). A coin nobody has looked at now tops out at **0.8**, by design.

The last **0.2** is craft, granted on `/review`:

    score = (factors ticked / 15) x 0.8   +   animation/100   +   coin/100

Everything ticked at 10/10 is exactly 1.0 and nothing else reaches it. **Nobody
types a score** - it is computed from what the reviewer ticked and slid, so the
number always arrives with its reasons attached, and unticking one box (say
"lettering reads correctly") visibly moves it. Clear restores the machine's
verdict; its number is never destroyed, it moves to `machine_score`.

Rescored to the new ceiling: luna / terra / grok **1.0 -> 0.8**, deepseek and sol
0.923 -> 0.739, hy3 -> 0.677, laguna -> 0.185. The four dead renders stay 0.0.
Rule #5 rebased and re-verified: reference **0.800** (machine max), empty 0.000,
flat disc 0.061.

**This is a deliberate trade.** The coin's headline number is now partly
subjective, which the rest of the suite refuses to be. That is the honest answer
for a task whose whole point is how something *looks*: the machine certifies it
is a real metallic turning struck coin, and a person says whether it is any good.
Every other task stays fully reproducible.

## 0.6.5 — attribution stops blaming us for traps; the coin stops failing good work

**Patch bump — scoring/classification fixes within v0.6.** No task content
changed; no archive. `harness rescore --tasks web-012-coin` applied.

### Falling for a trap was being credited as OUR bug

`rs-010-ants-rod` fired as `suspect-answer-key [harness]` because two strong
models both answered **'40'** — the *registered trap*. That verdict is attributed
to us, so it was **excluded from their attributed score**: claude-cli-opus-4-8
read raw 0.947 but **attributed 0.970** for falling into a trap the task exists
to catch. Meanwhile **six other models answered it correctly**, which proves the
key was fine all along.

Two fixes: `classify()` now checks registered traps **before** the suspect-key
heuristic (a trap answer is the expected wrong answer — it can never be evidence
of a bad key), and `suspect_answers()` stands down entirely when **anybody
scored above zero** on a task. The heuristic still fires where it should: an
unsolved task where strong models converge on one answer.

### "code ran but failed the checker's tests" — for an empty workspace

Adapters raise `kind="rumination_spiral"` for thinking with no output; assess
only matched `"runaway"`, so it fell through to `checker-fail`. opus's coin —
**300s of thinking, nothing emitted, empty workspace** — was reported as code
that ran and failed. Both spellings are matched now.

### The coin was failing good coins, again

- **`about_section` grepped for the word "about".** gpt-5.6-terra headed its
  brand story *"Made for the terminally online"*, sol likewise — both wrote
  exactly what was asked and both failed a test that was really demanding our
  noun. It now checks for a real prose block, which is the honest machine-check.
- **The margin assertion is gone.** The prompt asks the coin not to touch the
  canvas edge and that does make measuring easier, but it is OUR convenience,
  not a property of a good coin: terra and deepseek drew large, plainly-turning
  coins that fill the frame and lost a point for it. If a coin were clipped
  beyond measuring, the aspect spread flattens and fails on its own.

Rescored: **terra 0.846 → 1.000**, sol 0.846 → 0.923, hy3 0.769 → 0.846.
Reference and traps unchanged (1.000 / 0.000 / 0.077 / 1.000).

### Known-bad: the render lane is not reproducible for WebGL submissions

deepseek-v4-pro's coin scored **0.846 during its run and 0.077 on rescore — same
file**. Its page's WebGL context comes back `isContextLost() == true`
(`CONTEXT_LOST_WEBGL`), though nothing in its source calls `loseContext` and the
headless WebGL probe is healthy (ANGLE/SwiftShader, reads pixels). Chromium is
dropping the context, and whether it survives decides the score. **deepseek's
0.077 should not be trusted; re-RUN that one task rather than rescore it** —
a rescore replays in a different environment than the run measured.

Four separate heuristics for "which pixels are the coin" have now each been
fooled by a different model's decoration (luna's glow, sol's in-canvas caption,
terra's full-bleed, deepseek's context loss). The lane measures a dead render
correctly; its verdicts on *live* renders need a contract the model can't
decorate around — a v0.7 prompt change (expose the coin's geometry, require
`preserveDrawingBuffer`), since changing the prompt now would invalidate 11
models.

## 0.6.4 — web-012-coin was failing good coins; rescored

**Patch bump — scoring fix within v0.6.** No task content changed; no archive.
`harness rescore --tasks web-012-coin` applied.

The render lane's first real result was a **false negative**, and a big one:
gpt-5.6-luna built a coin that turns, carries a raking specular and a reeded
edge — a genuine **1.0** — and the checker scored it **0.3077**.

Two calibration errors, both from tuning against a single reference:

- **Silhouette detection bounded the backdrop, not the coin.** Thresholding
  colour-distance from a corner pixel looks obvious and is wrong: luna painted a
  soft glow behind the hero, the mask swallowed it, and the "silhouette" became
  the glow — whose aspect never changes. A coin that visibly foreshortens
  measured a spread of **0.009** instead of **0.337**, so `test_rotates_in_3d`
  failed, `_alive()` gated everything, and 9 of 13 tests fell over. Now the box
  bounds **strong-gradient** pixels: a coin has hard edges, a glow by
  construction does not. Robust to whatever a model paints behind, and it asks
  nothing extra of the prompt.
- **The relief bar sat inside the legitimate range.** Measured: blank is
  **0.00** (the flat trap), struck spans **5.6** (a subtle emboss) to **24.4**
  (a hard-struck one). The 6.0 threshold — picked off our own aggressively
  embossed reference — failed a real coin for being tastefully understated.
  Now 2.5, which is what actually separates struck from blank.

Reference and all three traps are unchanged (1.000 / 0.000 / 0.077 / 1.000), so
the gate did not loosen — the flat disc is still caught at 1/13.

**The lesson, recorded:** a threshold calibrated against one reference asserts
that every model will build like ours does. Reference-verification proves a task
can be passed and can be failed; it cannot prove the bar is in the right place.
Only real models do that, so the first results on a new task get eyeballed, not
trusted.

glm-5.2's 0.0 stands: it emitted no `app.html` at all (rumination-spiral).

### Content hashes were hashing bytecode (no bump — nothing tested or scored changed)

Chasing "glm passed web-002-maze in v0.5, why does it fail now?" turned up a
second thing: **the task content hash was never stable.** `hash_dir` walked
`rglob("*")`, so `__pycache__/*.pyc` counted as task content — merely *running* a
checker (python compiles it) changed the task's recorded identity. **33 of v0.5's
39 tasks recorded two or three different hashes for content that never moved**,
which makes `/info`'s "every result records a hash of the task" useless for
spotting real drift: you cannot separate a genuine task edit from a bytecode
cache. Caches are now skipped, and the hash is stable across a compile.

Repaired the 19 polluted hashes recorded in the live v0.6 dataset (18 in
glm-5.2's run, 1 in luna's) to the true content hash. Twelve of those were also
64 chars instead of 16: `tools/rename_tasks_v07.py` recomputed with `hash_dir(t)`
and missed the `[:16]` the runner applies — fixed there too. `archive/` is left
exactly as recorded; it is closed history, not a live claim.

*(The maze itself was not a regression: glm-5.2 blew the 32,768 ceiling on its
FIRST attempt in v0.5 too and only passed because the retry landed in ~18k. This
time both attempts ruminated through. Same budget, same two attempts, different
luck — the model sits right on the ceiling for that task.)*

## 0.6.3 — a provider rate limit is not a model failure

**Patch bump — scoring fix within v0.6.** No task changed; no archive.

kimi-k3's first run scored a raw **0.25**. It had scored **1.0 on every task it
actually reached** — ag-001, ag-002, py-003, all perfect. The other seven were
HTTP 429s: OpenRouter routes Moonshot through a shared key pool (`is_byok:
false`), and a model that shipped days ago is contended. Every one of those was
recorded as `score: 0.0, "run failed (all attempts errored)"`.

That is the no-op-floors-at-zero rule inverted: a **capability failure written
against a model that never got a turn.** The attribution engine caught it
(`rate-limit [infra]`, attributed score 1.0, 6 of 8 excluded) — but raw score is
what the matrix, standings and leaderboard read, so the headline number lied.

**A 429 now takes the same path a Claude usage cap already took**: drop the task,
write **no** `score.json`, let a re-run fill it in (aggregation is
latest-per-model·task). Three fixes:

- **`rate_limit` is its own error kind**, distinct from a 5xx blip, carrying the
  provider's `Retry-After` (header in seconds or HTTP-date, or a reset epoch
  parsed out of the 429 body).
- **The backoff was a joke.** `min(2 ** n, 15)` on the *retry counter* meant 2s,
  then 4s, then give up — ag-005 burned its entire budget in **16 seconds**
  against an upstream that said "retry shortly". Now it honours `Retry-After`,
  falling back to `10 * 2^(n-1)` capped at 60s.
- **A throttled provider stops the model, not the run.** After
  `RATE_LIMIT_STREAK` (3) consecutive drops, the model's remaining tasks are
  skipped and `run.json` is annotated `stopped_reason: rate_limit` — grinding on
  just drops the rest one at a time over hours, which is exactly what happened.

Nothing is scored as failure, so a re-run after adding your own provider key
fills only the gaps.

`tests/test_rate_limit.py` (9 tests) covers classification, `Retry-After`
parsing, the unwind, and that a plain 5xx still fails normally. Two bugs the
tests caught pre-ship: `time` was never imported in `adapters.py` (the body-epoch
path would have `NameError`d on the very 429 it exists to read), and
`RATE_LIMIT_STREAK` was referenced but never defined — it would have blown up on
the third consecutive 429.

Removed the killed kimi-k3 run: 7 of its 10 results were these fabricated zeros,
all 10 had 429 backoff inside `wall_ms` (so the timing was polluted too), and its
missing `finished` stamp was blocking every new run via `active_run()`.

## 0.6.2 — the render lane: a model's pixels get graded, not its shader source

**Patch bump. This is still v0.6** — 42 tasks, one added before the dataset had
ever been measured.

*This shipped as 0.7.0 first, and that was wrong.* Rule #4 bumps minor when the
test set changes, and web-coin took it 41 → 42, so the letter of the rule said
0.7.0. But the rule exists to stop results from two different task sets being
mixed — it protects **existing data**, and v0.6 had **zero runs**. Nothing had
ever been measured under the 41-task definition, so adding a task before any
baseline changed a dataset nobody could compare against. What the bump *did*
produce was a permanent hole: `archive/` holds v0.2, v0.3, v0.4, v0.5 and then
v0.6 would never exist at all, with the dataset everyone calls v0.6 filed under
0.7. Corrected to 0.6.2 (`tools/rename_tasks_v07.py`, which also restamps any
run manifest carrying 0.7.0). Lineage stays contiguous: **v0.5 → v0.6**.

### Task ids renamed onto the suite convention

The 11 v0.6 additions and web-coin ignored the `<prefix>-NNN-<name>` convention
every other task follows. Renamed, with the recorded results migrated in place
(the id is the aggregation key, so a naive rename would have orphaned them):

`ag-008-collections-fix` · `ctx-010-decoy-recall-32k` · `ctx-011-multihop-deep-32k`
· `ctx-012-aggregate-reversals-32k` · `rs-011-gear-axle-train` ·
`rs-012-permutation-track` · `web-007-life` · `web-008-snake` · `web-009-physics`
· `web-010-2048` · `web-011-sort` · `web-012-coin`

Retired numbers are not reused — the suite already skips ctx-001/002,
rs-001..005/007, py-001/002.

### New task — `web-012-coin` (one-shot-apps)

A one-shot WastedToken Mint site whose hero is a procedurally rendered challenge
coin: 3D turn, two struck faces, a reeded edge, and a metallic specular that has
to actually rake across the surface. Closes a real gap — all 11 existing
one-shot-apps are logic/state simulations (life, snake, physics, 2048, sort,
maze, sand, kanban, spreadsheet, expense, desktop). **Not one tested procedural
rendering, materials, or animation.** It also separates models that all "pass":
a gorgeous coin and a flat grey disc can otherwise score identically.

**Graded from pixels, never from source.** The checker pauses the model's loop,
steps a required `window.demo.setTime(t)` across it, screenshots the hero canvas
and measures the silhouette, the faces, the highlight and the rim. Plausible
shader code that renders a dead disc scores zero on every render test.

**The coin's liveness gates the whole task.** A first cut scored a flat grey
disc wrapped in a perfect site at **0.625** — the easy DOM scaffolding (four
tiles, a badge, an About paragraph) carried 10 of 16 equally-weighted points,
which inverts a task whose entire point is the render. So `_alive()` (the coin
turns in 3D *and* carries a metallic sheen — the doc's two most model-separating
criteria) now guards the gates and the site tests, the same way the agentic tasks
use `_guards_intact()`. A dead hero means the deliverable does not exist and
nothing else pays out.

Reference-verified (`python tasks-refs/web-012-coin/verify.py`):

| submission | score | |
|---|---|---|
| reference | **1.000** | 13/13 |
| empty | **0.000** | 0/13 — a no-op earns nothing |
| flat disc, perfect site | **0.077** | 1/13 — keeps only `test_demo_api`, which it genuinely satisfies |

**Honest limits, recorded so nobody re-litigates them:**

- *Whether the two faces show different motifs is not decidable from pixels.* A
  coin turned 180° transforms its motif as much as a different motif would —
  measured, a same-motif control differed from its own front by 17.2 mean luma
  vs the two-real-faces reference's 15.0. No threshold survives that. So
  `test_both_faces_are_struck` verifies each face carries real relief (high-pass
  energy of the face *interior*, so a plain disc can't score off its own
  outline), and claims nothing more.
- *Framerate is not scored.* Headless Chromium renders through SwiftShader
  (software), so a 60fps assertion would measure the rasteriser, not the model.
- WebGL/Three.js is fine: SwiftShader renders it, and being software it is
  deterministic — the same pixels every replay, which is what makes both this
  checker and archival video replay reproducible.

Two traps and a control ship in `tasks-refs/web-012-coin/traps/` so the verification
is reproducible, not a claim.

### Harness

- `pillow` added to requirements — the render lane decodes captured frames.
- Chromium in `.pw-browsers` is **149.0.7827.55**; renderer ANGLE/SwiftShader.
  Worth pinning: a stored `app.html` replayed on a future build could render
  differently.
- **Task titles are coerced to `str` at load.** `web-010-2048`'s meta said
  `title: 2048`, which YAML types as an int, and `html.escape()` on it threw —
  so the first report of any run containing that task died. Latent since the v0.6
  build: task report pages are only rendered for tasks *with results*, and
  `runs/` was empty until the first baseline. Fixed in the loader rather than by
  quoting the yaml, because a task's meta is content-hashed and editing it would
  invalidate results already recorded against it.

## 0.6.1 — the report stops looking like every other dashboard

**Patch bump — presentation only.** The task set and the scoring are untouched,
so 0.6.0 and 0.6.1 results aggregate into the same v0.6 dataset and nothing is
archived. Re-render with `harness report`; the operator panels need a server
restart + a tab reload to pick up the CSS.

### Overview rebuilt around the model·task matrix

The overview opened with the same vocabulary every LLM site ships: rounded stat
tiles, a ranked list, a stock scatter. It now opens with the object the data
actually *is* — the model×task grid. Cell fill ramps with the score; cell
**colour is the failure type**, read from the same `assess.classify` the model
pages use, so the two views can't disagree (amber = fell-for-trap, orange =
retrieval-miss, red = gave-up/DNF, hollow = excluded or not-run). The ranked rail
on the left is visibly just a *sorting* of the grid (rank · model · mean ·
gap-to-leader), and the footer row is the fleet average per task, so the hardest
columns read as dark gaps. Almost every leaderboard throws this matrix away; ours
is the honest shape of "latest result per model·task". Empty `runs/` degrades to
a "no runs yet" masthead with the grid hidden.

### One identity across every page

Rather than skin pages one at a time, the shared layer moved:

- Tokens promoted into `BASE_CSS` (`--hair`, `--rule`, `--mono`, `--miss`,
  `--cell-rgb`) so every page speaks one vocabulary.
- Hero stat tiles → an **editorial stat-line** (flex, hairline dividers, under a
  2px rule). Model / task / run pages followed with no markup change.
- Tables: mono uppercase headers on a `--rule` underline, `--hair` row rules,
  tabular figures; `.card` lightened to a hairline 6px.
- Section `h2` moved off sans small-caps — the generic-dashboard tell — onto the
  mono micro-label texture.
- Leaderboard podium flattened: hairline card, medal as a left-edge stripe.
- Operator panels (`/run`, `/backend`, `/manage`, `/datasets`) get the same
  treatment injected once via `_OP_CHROME`, which wins on source order.

### Score cells adopt the matrix swatch

Both score renderers (`_score_cell` for category averages, `score_chip` for
per-result cells) now route through one `_heat_swatch`: the same score-ramped
square the hero uses, followed by the number. State never rides on colour alone —
the number is tinted good/warn/crit and pending renders hollow. The category
table, per-task tables, run score grid and model comparison all read like the
hero. Verified on the v0.5 archive: 175 / 44 / 70 / 40 cells converted, zero old
chips left, click-to-sort still reorders.

### Output hygiene

Generated HTML no longer ships CSS/JS comments. Every surface (reports, operator
control pages, `studio` chart segments) passes through `strip_output_comments`,
which removes `/* */` and whitespace-preceded `//` while preserving `<!-- -->`
(our only ones are the functional navlinks/NAV injection markers) and any `//`
that follows non-space, so URLs survive.

### Failure attribution

Registered the `rs-gear-axle-train` trap in `directives.yaml`: meshing the shared
shaft instead of copying its rpm yields **108** (correct is 72). That miss now
classifies as `fell-for-trap` rather than a generic `wrong-answer`. The rest of
the attribution engine needed nothing — it derives from task category/lane, so
retiring and adding tasks can't make it stale.

## 0.6.0 — v0.5 archived; suite overhauled for differentiation

**Minor bump — the test set changed, so this is a new dataset.** v0.5 (35 models
× 39 tasks, all complete, dataset verified clean: 0.15% non-model results, 0
suspect answers) is archived immutably under `archive/v0.5/` — view it with
`harness report --dataset 0.5`. See docs/V0.6-PLAN.md for the full rationale.

**Retired 9 saturated tasks** (dead or near-dead — ≥ 33/35 models aced them, so
they carried little signal): ctx-001, ctx-002, rs-001, rs-002, rs-003, rs-004,
rs-005, py-001, py-002.

**Added 11 reference-verified tasks** (each: a known-good solution scores 1.0, a
no-op/empty scores ~0, before it counts) aimed squarely at the v0.5 weaknesses:
- **long-context** (was 88% aced — windows ace plain recall): `ctx-decoy-recall`
  (two-constraint match under near-duplicate decoys + supersession),
  `ctx-multihop-deep` (4-hop chain trace), `ctx-aggregate-reversals` (settled-only
  balance under pending/reversed noise). All ~32k tokens, generated so the key is
  correct by construction.
- **reasoning** (was 87% — memorized puzzles): `rs-gear-axle-train` (shared-shaft
  trap), `rs-permutation-track` (track one ball through swaps/rotations). Novel
  generated instances, program-computed answers.
- **one-shot-apps** (the discriminator — expanded from 6 to **11**): `web-life`
  (Conway's; trap = simultaneous update), `web-snake` (growth + wall/self
  collision + reverse-prevention), `web-physics` (gravity + bounce, stays in
  bounds), `web-2048` (slide/merge, one merge per tile), `web-sort` (incremental
  sort via a step API, not `Array.sort`). Behavioral Playwright checkers, each
  with a reference app.html that passes it.
- **agentic** (hardening via a new task on the ag-007 pattern): `ag-collections-fix`
  — 3 planted bugs (order-losing dedup, swapped partition, off-by-one windows),
  each target test guards all load-bearing behaviors so a no-op scores 0.

Suite is now **41 tasks** (agentic 8, coding-python 6, long-context 10,
one-shot-apps 11, reasoning 6). Guarded `tools/flip_v06.py` performed the
retire/add swap (refuses while any live run exists); the extra webapp + agentic
tasks were added directly, pre-baseline. **Pending: re-baseline the 35 models on
v0.6** (model runs = the operator's). Still open for follow-up
(docs/V0.6-PLAN.md): more in-place agentic hardening, and repeat-consistency
(`--repeat` on the hard set to populate the σ column).

### Cleanup: remove the orphaned time-chart code

Rolled up here: deleted the now-unused `timeline_chart` + `_short_run_label`,
simplified the overview model loop to build just the legend, dropped the dead
`.tl` CSS. (Zero output change; the charts were removed in 0.5.21.)

## 0.5.26 — the rank lens now shows the metric it sorts on

Presentation only. **No test or scoring change**, nothing archived.

The rank lenses (0.5.22) re-sorted the standings and renumbered `#`, but the
metric driving the order was **invisible** — only Pure (Score) and Value
(Score/$) lined up with a column; Speed, Efficiency, Hard and First-try sorted on
numbers shown nowhere, so the reorder looked arbitrary. Added a dynamic
**"Ranked by" column** (tinted, right after the model name) whose header and
values follow the active lens:

| Lens | Column header | Shows |
|---|---|---|
| Pure | Score | `0.997` |
| Value | Score / $ | `8,792.2` |
| Speed | Score / min | `5.57` |
| Efficiency | Efficiency | `frontier` / `dominated` |
| Hard tasks | Hard score | `1.000` (grok/glm on the discriminators) |
| First-try | First-try | `97%` |

The values are derived from the same `data-*` numbers the sort already used, so
there's one source of truth and no extra per-row data. The order now visibly
descends the tinted column. Verified all six lenses relabel + refill correctly,
`#` renumbers, no overflow.

## 0.5.25 — every score is 3 decimals, uniformly

Presentation only. **No test or scoring change**, nothing archived. Follows
0.5.24: rather than the 2/3-decimal hybrid (which left a ragged column and
disagreed with the standings' existing 3dp), **every score on the site now shows
3 decimals** — podium, standings (Score + Low), category chips, per-task score
grid, model/task/run tiles, family spans, bump-chart labels, scatter tooltips. A
true perfect reads `1.000`; a near-miss reads `0.997`; and two models clustered
at the saturated top (0.984 vs 0.976) stay distinguishable instead of both
collapsing to `0.98`. `_fmt_score` is now simply `{:.3f}`. Chart *axis* ticks
stay 2dp (they're scale labels, not scores). Verified no 2-decimal score display
remains.

## 0.5.24 — a 0.997 no longer reads as a perfect "1.00" + a "Low" column

Presentation only. **No test or scoring change** — the mean was always correct;
this stops the *display* from lying about it. Nothing archived.

A model with one 0.89 among 38 perfect tasks has a mean of **0.9972**, which a
two-decimal display rounded up to **"1.00"** — reading as a flawless sweep it
never earned. That rounded-up 1.00 is exactly the kind of number this project
exists to catch, and it was on the podium and the category chips.

- **Scores never round up to a fake perfect.** New `_fmt_score`: a genuine 1.0
  (every task perfect) shows `1.00`; anything below that which would round to
  1.00 shows **three decimals** (`0.997`) so it reads as the near-miss it is.
  Applied to the podium, the score chips, and per-task cells. (The standings
  Score column already showed three decimals, so it was already honest.)
- **New "Low" column** on the standings: each model's **worst single-task
  score**, with the task on hover — so a mean near 1.0 can't hide whether the
  one miss was a near-perfect 0.89 or a total 0.0. gpt-5.6-luna now reads
  score 0.997, **Low 0.89 (web-002-maze)**; gpt-5.6-sol reads 0.972, Low 0.00.
  Sortable, so you can find the models with a hidden zero.

### Speed & cost table: stop the unit columns wrapping

Energy ("222.83 Wh"), Peak VRAM ("26,352 MB"), Avg power ("304 W") and Cold
start cells could break between the number and its unit on a narrow column.
Added `nowrap` to those four (Tokens/Cost/Power-cost already had it).

## 0.5.23 — Tasks table: replace the saturated "Best" column with Aced / Spread

Presentation only. **No test or scoring change**, nothing archived.

The overview Tasks table's **Best** column listed every model tied at the top
score — a wall of names, since so many models ace so many tasks, and it said
nothing. Replaced it with two sortable numbers that instead *measure* that
saturation:

- **Aced** — models that scored a perfect 1.0, out of tested (e.g. `34/34`).
- **Spread** — `max − min` across models (`0.00` = everyone landed the same).

The table is now **sortable**, so it doubles as task triage: sort Aced ascending
and the real discriminators surface (`web-003-sand` 6/34, `web-002-maze` 7/34);
sort descending / spread 0.00 and the fully-saturated retire-or-harden
candidates surface (`ctx-002-recall-8k` 34/34, `rs-001`/`rs-002` 33/33). Verified
the values and the in-browser sort; no overflow.

## 0.5.22 — leaderboard rank lenses (Pure / Value / Speed / Efficiency / Hard / First-try)

Presentation only. **No test or scoring change**, nothing archived.

The standings table ranked on raw score alone, which saturates at the top. Added
a **"Rank by" lens** control that restacks the table AND renumbers the `#`
column, on metrics already computed:

- **Pure** — raw suite score (default, unchanged).
- **Value** — score per dollar (a local model's dollar is measured GPU
  electricity, so filter to one class to compare like-for-like).
- **Speed** — score per minute (quality per wall-clock time to reach it, not raw
  tok/s — that stays a sortable column).
- **Efficiency** — Pareto frontier first: a model not beaten on score AND cost
  AND tok/s leads; dominated ones sink. The leaderboard twin of the new scatters.
- **Hard tasks** — score on the discriminating subset (reuses the Discriminate
  page's computation), cutting through the ~0.99 top-end pile-up.
- **First-try** — share of tasks nailed 1.0 with zero retries.

The lens composes with the existing Local/Remote filter (e.g. Value+Remote ranks
API models by score-per-$), a caption explains the active lens, and blank metrics
sort last. Verified all six restack + renumber correctly and compose with the
filter. Numeric `first_try_val` / `score_per_min_val` / `score_per_dollar_val`
added to the summary for the sort keys.

## 0.5.21 — overview: kill the dead time charts, add value (cost/speed) frontiers

Presentation only. **No test or scoring change**, nothing archived.

The two "over time" charts were dead: with **one run per model** (32 of 33) they
were scattered dots, not a trend, and "hover to trace" traced nothing. Removed
both (the cross-version bump chart is the real longitudinal view). In their slot,
**value scatters** that answer "is a model worth its cost/speed":

- **Score vs cost** (API dollars to run the full suite; API/CLI only — a local
  model's dollar is just electricity, a different scale) and **score vs speed**
  (tok/s, with an All / Local / Remote toggle).
- Each draws the **Pareto frontier** and **dims dominated models** — one that's
  beaten on score *and* cost/speed by another. This surfaces what raw-score
  ranking hides: e.g. `claude-cli-opus-4-8` (0.969, $45) is dominated by
  `gpt-5.6-luna` (0.997, $0.79) — higher score, ~57x cheaper — yet raw score
  parks them a few ranks apart. The saturated top (best few within ~2-3%) is
  separated by cost and speed, not quality, and now the page shows that.
- Reuses the family page's aggregating-hover scatter; that hover JS is now **one
  shared handler** (`_SCATTER_HOVER_JS`) driving every `.szchart` on both pages,
  and the tooltip/legend CSS moved into `BASE_CSS` — no more per-page copies.

Verified: Pareto/dominated logic correct, cohort toggle filters, aggregating
tooltip fires on every scatter, family page still works, no mobile overflow.

## 0.5.20 — model page: the "why" sits next to the attribution

Presentation only. **No test or scoring change**, nothing archived.

On the model page's **Failure & retry assessment** table the "What happened"
explanation was the last column — after Attribution, Score and Retries — so on a
normal-width window the table's total width pushed it past the right edge into
the card's horizontal scroll, and you saw the attribution badge with **no
reason next to it**. Moved the detail to sit **immediately after Attribution**
(`Task · Category · Attribution · Why — what happened · Score · Retries`), so the
reason is adjacent and stays visible down to a ~900 px window (verified at 1280 /
1100 / 900). The far-right columns are now the short numeric ones, which is what
should clip if anything does.

## 0.5.19 — model page inline Why + operator chrome + serve --port default

Presentation + server. **No test or scoring change** — the Why column is derived
from existing results, the rest is server/CLI; nothing archived.

### Model page: inline Why (attribution) on the per-task table

The model page already had a "Failure & retry assessment" section with
attribution, but the main **per-task table** — where you scan each task's score —
had no Why column, unlike the task and run pages. So a failed row (e.g.
`web-002-maze 0.00`) didn't explain itself; you had to cross-reference the
separate section. Added a **Why** column driven by the same `diagnose` /
`why_cell` helper the task and run pages use (attribution badge + category, full
detail on hover), so the wording can't diverge. Verified on the latest run
(ornith-1.0-9b): all 13 non-passing rows now show their attribution inline
(rumination-spiral, retrieval-miss, partial, …).

### Operator pages: one canonical chrome (nav no longer wraps)

Server/UI only — **no bump**. The five operator control pages (Run, Watch,
Backend, Manage, Organize) each carried their own hand-maintained CSS block, and
those had **drifted**: body `max-width` was 980 / 1100 / 1200 across pages, `h1`
was 21 px on four and 22 px on Watch, and Watch's topbar used a different
alignment. On pages with a long sub-title (Watch), the `space-between` topbar
starved the nav of width and its links **wrapped to two lines**.

Fixed at the root, not per page: `_nav_page` — the single function every control
page passes through — now injects **one canonical chrome stylesheet last** (after
each page's own `<style>`, so it wins). It's the operator equivalent of
`report.BASE_CSS`: unified width, `h1`, and a nav that's a right-aligned flex row
which drops to its own full-width line *as a unit* when the title is wide (never
mid-nav wrap). Verified on all five pages at 1280 / 768 / 375 px: identical
chrome, single-line nav on desktop, **zero horizontal overflow at every width**
(also caught and fixed the Run page's flex `<h2>` toolbar overflowing on mobile).
Change the operator chrome once, here, and every panel follows.

### serve: `--port` remembers itself (`--save`)

Server/CLI only — **no bump** (no test, scoring, or report change). `harness
serve` / `review` already accepted `--port`; now `--port N --save` persists N as
the default so plain `harness serve` reuses it. Resolution: an explicit `--port`
wins for that run (one-off unless `--save`d); otherwise the saved default, else
the built-in 8765. The saved value lives in `settings.local.json` — gitignored,
per-machine, never in the public export. Documented in the README.

Made it discoverable from `harness --help` too: the `serve` line now flags
`--port / --save`, the typical-loop epilog shows the save form, and a new line
points to `harness <command> --help` for each subcommand's own flags (argparse
lists a subcommand's options only under that subcommand). Also dropped the
non-ASCII chars (em-dash, `×`) from CLI help and run output — they rendered as
`�` on Windows/cp1252 consoles.

## 0.5.18 — Capability-vs-VRAM chart: frontier legend + aggregated hover

Presentation only. **No test or scoring change**, nothing archived.

Two fixes to the Families page scatter, both from a confused reading of the
chart:

- **The dashed line now has a legend.** It's the **Pareto frontier** (best score
  reachable at each VRAM budget) — it only *looked* like a "Gemma line" because
  the Gemma models happen to sit on the frontier. There was prose about it below
  the chart but no visible key, so it read as an unexplained line tied to one
  family. Added an on-chart legend above the plot: a dot swatch ("a local
  model") and a dashed swatch ("Pareto frontier — best score per VRAM").
- **Hover now lists every dot under the cursor.** Overlapping dots (e.g.
  gemma-4-31b and ornith-1.0-35b sit ~17 px apart) previously hid each other —
  an SVG `<title>` only shows the topmost element's. Replaced the per-dot
  `<title>` with a proximity handler: on mousemove it maps the cursor to chart
  space and lists **all** dots within 16 px, nearest first, in one tooltip.
  Verified: isolated dot → 1 line, the overlapping pair → both, hides on leave,
  no console errors.

## 0.5.17 — Families page follows Organize (No-family models excluded)

Presentation only. **No test or scoring change**, nothing archived.

The Families page now mirrors the **Organize** page: a model appears only if it
belongs to a family. Previously a model set to **No-family** (`family: none`,
which resolves to an empty family name) fell through a `... or model_name`
fallback and showed up as its own **singleton family** — so the No-family
models (agents-a1, north-mini-code, hy3-free, laguna-xs-2.1, minicpm5-1b,
nemotron) littered the page as one-member lineages. `family_stats` now skips any
model whose resolved family is empty, so it's dropped from the champions table,
the within-family cards, and the Capability-vs-VRAM scatter at once. Assign a
family on Organize and it reappears; move it to No-family and it's gone. Intro
copy updated to say so. (Models with an *unset* family still infer from the name
as before — only the explicit No-family sentinel is excluded.)

## 0.5.16 — live operator nav on every page + mobile/tablet responsive

Presentation + server only. **No test or scoring change**, nothing archived.

**Operator nav no longer drifts.** Control pages (`/run`, `/backend`…) inject
their menu live per request; report pages (Overview, Discriminate, Family,
model/task/run) were served as static files carrying whatever nav was *baked
in*, so the two could diverge — Overview could show a stale/short menu while Run
showed the full one. Now the operator server **re-injects the live nav** into
report pages too (marker-wrapped `<!--navlinks-->…`, prefix computed from the
page's depth), so every operator page reaches every destination and the menus
are always identical. Static files keep a self-contained baked nav for
public / GitHub-Pages hosting (archived-dataset pages are left as baked — their
nav is intentionally scoped to their own directory).

**Mobile / tablet / iPad.** Verified empirically (real computed layout at 360 /
375 / 768 px, both themes) that pages no longer overflow sideways:
- **Every table becomes its own horizontal scroller** on ≤760 px
  (`display:block; overflow-x:auto` — the grid stays intact via anonymous table
  boxes), so even a table not wrapped in a `.card` can't blow out the page. This
  fixed the Family "within each family" tables and the Info glossary tables
  (was 305 px / 89 px of overflow at 375 px → 0).
- **The header stacks and the nav wraps** on narrow screens — the nav was a flex
  item sizing to its one-line max-content (≈413 px), so its links never wrapped;
  now the topbar goes vertical and the nav is a wrapping flex row.
- Tighter phone gutters (30 px → 15 px). Same responsive rules injected into the
  operator control pages via `_nav_page`, so panels behave identically.

**Cross-browser.** Audited the CSS for fragile modern features — none found
(no `:has()`, `color-mix`, `clamp`, `@container`…). Only broadly-supported
primitives (custom properties, flexbox/grid, `prefers-color-scheme`, SVG
`viewBox`, flex `gap`), so current and reasonably-old Chrome / Firefox / Safari /
Edge, plus iOS and Android, all render correctly in both light and dark.

## 0.5.15 — site-wide table centring (every page, operator + public)

Patch bump. **No test or scoring-methodology change** — presentation only, the
"0.5" measurement is unchanged and nothing is archived. 0.5.14 centred the
family/champions tables; this finishes the job everywhere, driven by an
automated per-column audit (compare each header's computed `text-align` to its
first data cell across every table, on every rendered page, in an iframe with
real CSS applied — not a source grep).

- **The root-cause CSS bug.** The base rule left-aligned `td.nowrap`, which
  *came after* `td.num` in the stylesheet — so any numeric cell that was also
  nowrap (`class="num nowrap"`: the Tokens / Cost / Power-cost columns, per-task
  Score chips, the discriminating-tasks leaderboard) lost its centring to the
  later, equally-specific `.nowrap` rule. Name cells are left by default anyway,
  so `td.nowrap` was both redundant and harmful; dropped it. Now `.num` wins for
  every numeric cell regardless of nowrap.
- **Remaining ragged columns fixed** found by the audit: the standings VRAM/fit
  cell (no `.num`), the model page's per-task Score chip, the task page's
  per-model Score chip, and the redundant-task-cluster `r` header (a bare `<th>`
  centring `1.000` cells beneath a left header). All now align header-to-cell.
- **Verified on every page type** — overview, discriminate, family, info, model,
  task, run — with **zero** header/cell mismatches, and re-verified on the
  **public export** (same templates, read-only nav, GitHub-Pages-relative links).
  Operator control panels (Run / Backend / Manage / Organize) are uniformly
  left-aligned status tables by construction — no numeric columns to misalign.

## 0.5.14 — model details, family/VRAM polish, public-export correctness

Patch bump tagging the batch below. **No test or scoring-methodology change** —
the "0.5" measurement is unchanged and nothing is archived. Highlights: per-model
**details card** (quant / context / VRAM / links); real **VRAM-to-run**
(weights + KV cache) on the family chart, family table, model page and standings;
**family colour** manager + slighter member shades; one **unified header** on
every page (report AND operator); the **public export** now regenerates pages
with the read-only menu (no dead control links); and `harness --help` / README
polish for the public release.

### model details card + HF/OpenRouter links + harness --help + README

- **Model details on the model page.** A "what we tested" card: model id, quant,
  max context, architecture, publisher, weights + VRAM-to-run, the generation
  budget (max tokens · temperature) it ran under, list price / gateway host for
  hosted models — plus **reference links** to Hugging Face (local weights) and
  OpenRouter / Anthropic (hosted), direct when the id is a clean repo path, a
  search otherwise so a link is never dead.
- **`harness --help`** now has a real description, a typical-loop epilog, and a
  note that operator commands appear only with the private layer — and it's
  automatically public-vs-operator aware (the public build omits them).
- **README**: a "Viewing & sharing the results" section (run the read-only
  viewer, or host `reports/` as static files on any web server / GitHub Pages)
  and a "Public vs operator" section (the public export is the full runnable
  harness incl. `harness.ps1`; the control panel stays private).

### family page polish + real VRAM (weights + KV cache) on the charts

Fixes and an upgrade on the public Families page:

- **Black axis text fixed.** `--ink-dim` was never defined, so SVG
  `fill:var(--ink-dim)` fell back to black. Defined it (dimmed ink) in the base
  CSS — fixes the chart axis label and every `.note` that used it.
- **Hover tooltips on the scatter.** Each dot now has a large transparent
  hit-target with a `<title>`, so mousing over reliably shows the model name and
  its VRAM/score breakdown (the tiny r=6 dot was hard to hit).
- **Centred data columns.** The family + champions tables had numbers
  right-aligned under left-aligned headers (ragged). Data columns (members,
  score, VRAM, tok/s, best) are now centred; names stay left.
- **Real VRAM, not just weights.** The "Capability vs VRAM" x-axis and the
  per-model **VRAM @32k** column now show the VRAM to actually RUN a model =
  weights (from the quant) **+ KV cache** at 32k context (`gguf.footprint`),
  with the weights/KV/quant breakdown on hover. That's the "what card do I
  need" number. (The standings GPU-fit gate already computes this live.)

### public export: regenerate pages with the public nav

The export was *copying* the operator-generated `reports/`, so the shipped pages
carried the operator nav — dead control links (`/run`, `/watch`, …) that 404 on
static hosting. `tools/export_public.py` now **regenerates** the whole site into
the export with `public_nav=True` (live dataset + every archived dataset via
`render_dataset(..., public_nav=True)`), so exported pages show only the
read-only menu (Overview · Families · Discriminate · Info). The one body
reference to the Run page in the overview foot is dropped in public builds too.
Verified: zero control links across overview / family / discriminate / info /
task / model / archived-dataset pages; the operator site keeps the full menu.

### family colours: tighter, slighter member shades

Members of a family now vary only *slightly* in lightness around the family
colour (a capped span centred on it) instead of spanning dark→pale — so a
2-model family like GPT reads as two close reds, not dark-red vs pink, and a
5-model family stays clearly one colour. A lone member is the exact family
colour.

## 0.5.13 — reporting & analysis overhaul (families, diagnosis, nav, palette)

Patch bump tagging the batch below. **No test or scoring-methodology change to
the live suite** — the "0.5" measurement is unchanged and nothing is archived.
What it packages (detail in the `###` sections): the model **families** page +
the operator **family manager** (kanban) + **family-hued palette**; the
**`/discriminate`** page and the "who's actually best" hard-subset board;
**local/remote + GPU-fit** drill-down; the task-page **Why** column with the
`assess` taxonomy fixes (0 unknown-errors); **runaway-generation** handling and
**reasoning-token** capture; one **shared nav** with a public-only menu; the
tier-aware **Tries / turns** label; and the **fastest/fewest-tokens** tiles now
counting only passes.

### family manager — a kanban to organise models + colours (operator)

New operator page **`/families-edit`** (nav: *Organize*) — a drag-and-drop board
to curate model families and their chart colours:

- Columns are families (auto-seeded from the inferred families) plus a **No
  family** column. Drag a model card between columns; **+ New family** adds a
  column; deleting a family drops its models into No family.
- Each family has a colour swatch — its colour governs all members (shades per
  member on the charts). A **No-family** model takes its own colour, or an auto
  hue from the palette (one not used by a family) if none is set.
- **Save** writes each model's `family:` / `color:` into its yaml and the family
  colours into `families.yaml`, then re-renders — presentation only, never
  touches a score or an in-flight run.

Plumbing: `registry` gains `load_families` / `save_families` /
`set_model_family` / `set_model_color` and a `family: none` sentinel for
explicit No-family; `_model_colors` now takes manual family colours (hex →
HSL, with member shades and a lone member = the exact colour) and falls back to
golden-angle auto-hues that steer clear of the manual ones. `families.yaml` is
on the public export allowlist so the shipped site shows the same colours.

### one shared nav on every page + public menu + family-hued colours

Three related fixes.

- **Consistent navigation.** Every page hardcoded its own nav subset, so the
  task/model/run pages showed only "Overview · Run · Info" while the overview
  had the full menu. There is now ONE nav (`report._nav`) rendered on every page
  — Overview · Families · Discriminate · Run · Watch · Backend · Manage · Info.
- **Public menu differs by build.** The read-only public build
  (`generate_all(public_nav=True)`, used by `viewer.serve`) drops the
  operator-only control links, leaving Overview · Families · Discriminate · Info.
  So a GitHub visitor gets a clean menu with no dead control pages; the operator
  server keeps the full set. (Static links are relative so they work on GitHub
  Pages / file://; control links are absolute server routes.)
- **Family-hued auto palette.** When a model has no manual `color:`, it is now
  coloured BY FAMILY — each lineage gets its own hue (golden-angle spread) and
  its members distinguishable shades, so "all the Gemmas" read as one colour
  group across every chart. A yaml colour override still wins. (Colours are
  HSL at mid-lightness; a manual override is still the way to pin an exact hue.)

### task-page "fastest / fewest tokens" now count only passes

The task page's **fastest** and **fewest tokens out** tiles were min'd over
EVERY model, so a model that errored in 4s or emitted 12 junk tokens took the
crown (e.g. ctx-009: "fastest" was qwen3-32b at 4.5s scoring 0.0; "fewest
tokens" was gemma-3-4b at 12 tokens scoring 0.0). They now consider only results
that PASSED (score >= the 0.8 site pass threshold), and are relabelled
**fastest (passed)** / **fewest tokens (passed)**. ctx-009 now reads minimax-m3
4.6s and sonnet-5 41 tokens, both 1.0. Checked the rest of the site: this
min-over-failures pattern existed nowhere else (the tps chart axis-max is just
scaling; the fit "value pick" already filters by threshold). Presentation only.

### deciphered failure reason on the task page + taxonomy fixes

**Task page gains a "Why" column** — for every non-passing model, the deciphered
reason (`assess.classify`): an attribution badge (model / harness / infra /
known-limit) + the category (rumination-spiral, fell-for-trap, retrieval-miss,
checker-fail, context-overflow, …) with the full hand-diagnosis on hover, and in
the "what each model produced" detail. Same taxonomy the model page already
uses, now shared via `report.diagnose` / `report.why_cell` so wording never
diverges. This complements the symptom badge (⟳ runaway / ⧖ timeout) with the
precise cause.

**Taxonomy fixes** (`assess.classify`) so nothing lands in the catch-all — the
suite had 13 `unknown-error` results, now **0**:
- **context-overflow** now matches the many ways providers word it ("context
  size", "exceeds the available/maximum context", …), not just "window/length".
  The 128k-task failures on small-window models are now correctly known-limit.
- **runaway** (our loop-guard / ceiling-hit-with-no-answer signal) is decoded
  explicitly as a model rumination-spiral, even when the run's summary was generic.
- an all-attempts **format** failure that errored out with a generic summary is
  recovered as `format-miss` (model) — but a ceiling-hit (`stop==length`) stays
  a rumination-spiral, not a format slip.

Side effect (a correctness gain): those 13 were formerly attributed to `infra`
and **excluded** from the attributed score, quietly inflating the affected
models. They now count (known-limit and model failures are real signal), so a
few attributed scores drop slightly to the honest value. Presentation/analysis
only — raw scores, the leaderboard, and the dataset are unchanged.

Also: the **model names on the task page are now links** to each model's page
(both the comparison table and the full-history table), matching every other
table on the site.

### model page: tier-aware "Tries / turns" label (presentation)

The model page's per-task **Tries** column read as a contradiction: an agentic
task could show "5 tries" next to "0 retries". The number was right — for a
tier-2 agentic task it's the count of **turns in the tool-use loop** (each turn
is a request, not a re-try) — but "Tries" made it look like failed attempts.
Now the column (`_effort_label`, renamed **Tries / turns**) is tier-aware: an
agentic task shows `5 turns`; a single-shot task shows `1` or `1 + 2 retries`.
Header tooltip and the page foot spell out the distinction; sorting still uses
the numeric value.

### capture reasoning-token counts (run-engine)

Records how many tokens a model spent in its think channel, so a runaway zero
can be read: a **high** reasoning count with empty content = the model ruminated
its whole budget away without concluding; a **low/zero** count with a full
`tokens_out` = it emitted empty/garbage content directly. This is the laguna-xs
question (small hosted model looping on the parsing tasks) made answerable.

`ChatResult` gains `reasoning_tokens`, taken from the provider's usage
(`completion_tokens_details.reasoning_tokens` or `reasoning_tokens`) and, when
the provider streams a think channel but doesn't count it, estimated from the
streamed chars (~4/token). Summed into `metrics.json`, kept per-attempt, and
logged on each transcript `response` event; the task pages show "· N think"
beside tok-out when present. Applies to future runs (a run already in flight
predates it — re-run a model to capture it, latest-per-task supersedes). Tests
in `tests/test_runaway.py`.

### model families page + score-vs-VRAM Pareto (presentation)

New **`/family` page** (nav link next to Overview) grouping models by lineage,
so a family's size↔capability ladder is legible and a small local model can be
read against its larger hosted sibling:

- **Within each family** — members sorted by score with a bar, where they run
  (local ⚡ / hosted), weight size (GB, from the GGUF), and tok/s. A
  "local + hosted" tag flags families you can compare across that line (e.g. GPT:
  `gpt-oss-20b` vs `gpt-5.6-terra`). The Gemma ladder immediately shows the
  quant-quality gap — the Q4_0 QAT build sits ~0.46 below the standard build at
  the *same* 17 GB.
- **Best of each family** — a champions table ranking lineages by their
  strongest member.
- **Slice 4 — Capability vs VRAM** — a scatter of local models (score vs weight
  GB) with the **Pareto frontier** drawn: the best score reachable at each VRAM
  budget. A dot below the line is beaten by something smaller.

Family is set by a yaml `family:` key, else inferred from the name
(`registry.infer_family`); an unrecognised model is its own family until a
`family:` is set. `/family` is served by both the operator server and the public
read-only viewer. Tests in `tests/test_discriminate.py`.

**`/discriminate` gains a "who's actually best" board** (the other half of Slice
4): models ranked on ONLY the genuinely-separating tasks (frontier-hard +
wide-spread discriminators — currently just 3: py-004, web-002, rs-010), with
each model's **move vs its global rank**. It reshuffles hard: qwen3-32b climbs
+15, qwen3.6-27b to #2, while fable-5 drops -11 and opus/sonnet-5 drop -7 —
they were riding the easy tasks. That it can only rank on 3 tasks is the honest,
vivid case for the v0.6 frontier-task work.

## 0.5.12 — run-engine, presentation & tooling roll-up

Patch bump tagging the batch below. **No test or scoring-methodology change to
the live suite** — the "0.5" measurement is unchanged and nothing is archived;
this version just marks a coherent release point. What it packages:

- **Run-engine:** the claude process-tree kill (fan bug), and runaway-generation
  handling (retry cap + mid-stream loop guard + `failure_mode` badges). Future
  runs are cheaper and their failures legible; past scores are untouched.
- **New views:** the `/discriminate` page, local/remote standings + task-fit
  drill-down, and the GPU-size fit gate; the bump chart now shows every model.
- **Archive honesty:** the v0.4 control-token re-score of north (a scoring-bug
  fix on frozen data, documented in `archive/v0.4/PROVENANCE.md`) + the pre-v0.5
  methodology caveat on archived pages.
- **Packaging:** public-release Phase 2 — the read-only `harness/viewer.py`.

Detail for each item is in the entries below.

### public release Phase 2: read-only viewer

`harness serve` now works in the public export without shipping the control
panel. New **`harness/viewer.py`** is a read-only results server: the static
site (overview, per-run/task/model pages, `/info`, `/discriminate`), the dataset
switcher (`/api/versions`), and read-only browsing of `runs/`. No control routes
and no POST — a publicly-deployed instance can't spend a subscription or mutate
data. Control-nav links (`/run`, `/watch`, `/backend`, `/manage`) resolve to a
short "operator-only" stub instead of a dead 404.

`serve` is defined once in the public `__main__`; when the private
`_control_cli` is present it **overrides the handler** with the full control
server (`review.serve`) and adds the `review` alias — so the operator's
`harness serve` is the control panel and the public one is the viewer, decided
purely by which files shipped. `viewer` is on the export allowlist and the
boundary test; it imports only `config`, `report`, `archive`. Verified: viewer
serves `/` and `/discriminate` (200), `/api/versions` (200), `/run` (stub),
`/api/models` (404), `POST /api/run` (405); export ships `viewer.py`, holds back
`review.py` + `_control_cli.py`, and passes the no-private-imports check.

### discrimination page + local/remote drill-down (presentation)

Making the numbers more useful, no dataset change.

- **New `/discriminate` page** (`report.build_discriminate_page`). A leaderboard
  says who won; this says *which tasks the answer depends on*. Per task: mean,
  spread (σ), %1.0 / %0, and the gap between the strongest and weakest cohort,
  with a verdict badge — dead / ceiling / floor-gate / discriminator /
  **frontier-hard** (even the best struggle). Headlines the frontier
  compression (top-8 within 0.04 → their order is mostly noise) and lists
  redundant task clusters (pairs that rank models identically, r > 0.985) as
  collapse candidates. Nav link on every page. All derived from live runs.
- **Standings table, filterable by where a model runs** (All / Local ⚡ /
  API-CLI). Local and API models are different constraint classes, so a combined
  mean is apples-to-oranges — the reader narrows to theirs. Includes a
  **score-per-dollar** value column (a local model's dollar is measured GPU
  electricity, marked ⚡).
- **Task-fit is cohort-aware** (All / Local only / API-CLI only). The picks are
  *recomputed* per cohort, not just hidden — so "best local model for reasoning"
  is a real answer, not the global winner with rows removed.

- **GPU-size fit gate on the Local standings.** Selecting **Local** reveals a
  "fits my GPU" control (VRAM size × context). Each local model's weights + KV
  footprint is read from its GGUF at report time (`gguf.footprint`, sharing the
  KV math with the fit advisor via a new `_kv_components`) and baked into the
  row, so the gate computes `weights + kv_fixed + kv_per_tok·ctx` client-side —
  showing the VRAM needed at your context and whether it fits, with an optional
  "hide models that don't fit". This is the honest basis (measured from the
  model file), unlike peak VRAM which is entangled with the run's loaded window.

Tests: `tests/test_discriminate.py`.

### runaway-generation handling (run-engine + presentation)

A bad quant (or a model ruminating forever) burns its full token ceiling and
emits no answer. The gemma-4-26b-a4b-QAT/Q4_0 run made this concrete: 20 of 39
tasks failed by generating 32,768 tokens of nothing — three times each, because
each no-answer attempt was retried like a formatting slip. Four fixes:

- **Retry cap on runaways.** `_chat_with_retries` now recognises a generation
  that hit the token ceiling (`stop_reason == "length"`) yet failed validation
  as a *runaway* and allows only ONE retry, not `task.max_retries`. Rare flukes
  still recover; the pathological case stops burning ~2/3 of the wall time for a
  guaranteed zero. A normal format miss (model stopped, formatted wrong) keeps
  the full retry budget.
- **Mid-stream loop guard.** The streaming adapter watches the combined
  content+reasoning stream and aborts when a short cycle repeats back-to-back
  (`adapters._LoopGuard`) — killing the loop before it reaches the ceiling.
  Tuned to fire only on strong evidence, so tables/boilerplate don't trip it.
- **`failure_mode` on every result** + a report badge (⟳ runaway / ⧖ timeout /
  ⇥ max-turns / ⚠ error) on the task pages, so a runaway reads differently from
  a wrong answer. Derived for older runs too; gated on a failing score so a
  truncated-but-graded answer is never mislabelled a runaway.
- **Fairness confirmed (with a test):** reasoning tokens are excluded from the
  graded answer — a model that spends its budget in the think channel yields an
  empty answer and scores 0 as "no answer", never has its reasoning graded.

Run-engine + presentation only; no dataset change. Tests: `tests/test_runaway.py`.

### v0.4 archive honesty pass (data correction + caveat)

Two things, both about being truthful across versions. No live-dataset change.

- **Corrected a scoring BUG frozen in the v0.4 archive.**
  `coherelabs.north-mini-code-1.0` had 13 answer-lane results scored `0.0` that
  are actually `1.0`: it emitted correct answers with a trailing control token
  (`<|END_OF_TURN_TOKEN|>`), and the v0.4-era `extract_answer` couldn't parse
  past it. v0.5.7 fixed the extractor (task-agnostic), so re-parsing the SAVED
  outputs is deterministic — the same operation `harness rescore` runs live.
  North's v0.4 suite mean rises **0.339 → 0.758** (rank ~22 → 20). It is the
  only model affected (sole control-token emitter; the correction tool aborts if
  any other model would change). This is a bug fix, not a rewrite of history —
  the task definitions were untouched. Tool: `tools/correct_v04_north.py`
  (dry-run by default). Documented in `archive/v0.4/PROVENANCE.md`.
- **Added a methodology caveat to pre-v0.5 archived pages.** The no-op-floor
  fixes (v0.5.5–0.5.6) and timing calibration (v0.5.9) were *task/checker
  redesigns*, so they can't be retro-applied to frozen datasets without
  pretending v0.4 used methods it didn't. Instead of rewriting, the archived
  overview pages (and the bump-chart note) now carry a banner: weak-model scores
  on agentic/timing tasks before v0.5 can be over-credited; ranks stay the
  honest cross-version comparison. Presentation only (`report._pre_v05_caveat`).

### bump chart shows every model (presentation, no bump)

The rank-across-versions bump chart used to hide any model that appeared in
fewer than two dataset versions, so a model with a single run vanished entirely.
Now **every model that ever ranked is drawn**, a single run showing as a lone
dot:

- A model **present in the latest version** is drawn exactly like the others —
  dot(s) plus a name label at the right edge.
- A model that lives **only in archived data** (not in the newest dataset) has
  no persistent label — it would float mid-chart pointing at a dead line —
  so its name comes up on **hover** instead.
- Every node also gains a native `<title>` tooltip, so hovering any dot names
  the model(s) sitting at that rank (helpful where tied models overlap).

### kill the whole claude process tree (fan bug)

Run-engine fix, no dataset change. **Symptom:** after a run finished, one CPU
core stayed pegged and the fan kept roaring; killing the `serve` process stopped
it *instantly*.

**Cause:** `claude -p` is a launcher — a single invocation forks a whole tree of
worker processes (a dozen-plus children under the top `claude`). When a task hit
the time budget or the rumination-spiral cutoff, the adapter's cleanup called
`proc.kill()`, which on Windows is `TerminateProcess` — it reaps **only the
direct child**. The worker subtree was orphaned, and a worker kept **busy-looping
a full core** for the rest of its would-be run. It only died when `serve` (its
console owner) was torn down, which is why killing serve stopped the fan at once.

Verified empirically: `proc.kill()` on a parent left its busy-loop grandchild
`STILL_ACTIVE`; `_terminate_tree` takes out the whole subtree.

**Fix:** `harness/adapters.py` gains `_terminate_tree(proc)`, called from
`_stream_claude_cli`'s `finally` instead of `proc.kill()`. On Windows it runs
`taskkill /F /T` (walks the live parent→child snapshot — so it must fire while
the top process is still alive, which it is on the timeout/spiral raise); on
POSIX the subprocess gets its own session (`start_new_session=True`) and the
whole group is `killpg`'d. Regression test spawns a real parent→grandchild busy
loop and asserts the grandchild is gone after `_terminate_tree`
(`tests/test_usage_limit.py`).

### pricing disclaimer

- **`/info` gains a Pricing section**, because the cost column was quietly
  overclaiming. The numbers are **derived from the live runs**, so they can't go
  stale:
  - **76% of cost figures (624 of 819) are computed from a list price captured
    when the model was registered** — a snapshot, not a live rate. Providers
    change prices; the site does not notice. Only the 24% where the gateway
    reported an actual billed amount (marked ✓) are authoritative.
  - **The same model is served by different providers at different prices.**
    OpenRouter routed this catalog to **23 different upstream hosts** (Novita,
    Nvidia, Baidu, Together, Fireworks, DeepInfra, …), which differ in price *and*
    quantization — so a model's cost, and its score, can move between runs without
    the model changing at all.
  - **Claude subscription runs report the API-equivalent price**, not what the
    subscription actually costs you.
  - **Local models are not free** — no money changes hands, but a run drew ~480
    Wh. Compare locals on *energy*, not on `$0.00`.
  - Bottom line: cost is sound for order-of-magnitude comparison *within* a
    dataset; it is not a budget, a vendor quote, or comparable across dates.

### pin the models, name the version

The suite content-hashes every TASK but pinned no MODELS. `claude-cli-sonnet`'s
yaml said `model: sonnet` — a moving alias that resolves to **claude-sonnet-4-6**.
Every "sonnet" result in the dataset is Sonnet **4.6**, not Sonnet 5. Anthropic
could repoint that alias tomorrow and the longitudinal charts would never notice:
the silent-version-swap problem, inside the suite that exists to catch it.

- **Registration now resolves and PINS.** `add claude sonnet` asks the CLI what
  the alias actually resolves to, pins the concrete id, and names the model after
  the version it really runs. The yamls are pinned:
  `claude-sonnet-4-6`, `claude-opus-4-8`, `claude-haiku-4-5-20251001`.
- **Sonnet 5 registered** (`claude-cli-sonnet-5` → `claude-sonnet-5`) — a model
  that had never been run. Any other version, new or old, can now be added the
  same way: `harness add claude <alias-or-full-id>`.
- **`harness rename-model old new`** — a model's NAME is its identity here
  (aggregation is latest-per-model·task), so a misleading name can't just be fixed
  in the yaml without orphaning its history. This moves the registry entry AND
  every `runs/<run>/<model>/` directory, rewriting the `model` field inside each
  metrics.json so the data is self-describing. Dry-run by default; **refuses while
  a run is executing** (renaming a directory mid-write loses measurements).
- **The version is displayed with the name** on every leaderboard placard — for
  Claude and everything else (`claude-sonnet-4-6`, `qwen/qwen3.6-27b`,
  `z-ai/glm-5.2`). A label is not a measurement.

Pending: bank the sonnet history as `claude-cli-sonnet-4-6` once the live run
finishes (39 results across 3 runs — the tool is guarded and dry-run verified).
Archived datasets (v0.2–v0.4) are deliberately NOT relabelled: those runs
predate this capture, so what their alias resolved to is genuinely unknown, and
asserting "4.6" would be inventing data.

### model watch UI + a cross-process run lock

- **Watch hides models you already run.** The poll built candidates purely from
  OpenRouter/HF and never checked your registry, so a model you'd already
  built — claude-sonnet-5 — kept showing up as NEW with a live Scout button.
  Now any candidate matching a registered model is dropped from the list (matched
  across id forms: OpenRouter's `anthropic/claude-sonnet-5` == your CLI's
  `claude-sonnet-5`, a `:free` suffix folds to its base). The header notes how
  many were hidden. Watch is a page of models to CONSIDER adding; a model you've
  built isn't a candidate.
- **Models now have a lifecycle: Build / Scout / Promote / Dismiss.** `/watch`
  candidates get two buttons — **+ Build** (register a model you're sure about; it
  joins the fleet enabled, and you launch runs yourself) and **Scout** (register it
  PARKED/disabled + run the 5-task screen). Both drop the model off the candidate
  list on refresh. A new **"Scouted — needs review"** panel shows each scout's
  verdict and per-task scores with **Promote** (enable it → fleet member) and
  **Dismiss** (park it, stop nagging); a re-Promote is available on dismissed ones.
  Decisions live in `scouts/decisions.json`, separate from the verdicts so they
  survive a re-scout. Nothing auto-*runs* — Build and Promote make a model
  available; you always launch runs from /run.

- **Scout is now triage, not a dataset entry.** It used to write straight into the
  versioned `runs/` pool tagged "scout" — so a 5-task screen leaked into the
  leaderboard and became "latest per model·task". Now scouts live in a separate
  **`scouts/`** tree (gitignored) that aggregation never reads: a scout can no
  longer touch the dataset. It still holds the one-run-at-a-time lock while it
  executes (it uses the same GPU/CLI), because `active_run()` watches `scouts/`
  too. Each scout produces a **verdict** from thresholds in `directives.yaml`:
  **PROMOTE** (≥0.6 mean — worth a full run), **BORDERLINE** (≥0.35), **SKIP**.
  `/watch` shows recent verdicts with a **Run full suite** button on promotes;
  `harness scout <model>` prints the verdict inline.

- **Scout now registers the model for you**, which is what it should have done
  all along — before, it 404'd unless you'd already added the model on the
  Backend page. A click now routes by access: a **Claude** model is registered
  via the CLI subscription (pinned to its concrete version); anything else served
  on **OpenRouter** is registered through your OpenRouter key, with pricing
  auto-filled from the catalog; then the scout run starts. A **local-only gem**
  (trending on HF, served by no API you have) can't be auto-registered — the card
  says so and points you to pull it in LM Studio. The UI reports how it was
  registered ("registered claude-cli-sonnet-5 via the Claude CLI · scouting…").


- **`/watch` page** — the discovery engine finally has an interface. Shows
  **SCOUT / GEM / NEW / FADING / LOCAL-FIT** with usage rank, 30-day token share,
  HF trend, and the VRAM verdict; a **Poll now** button (network-only, safe during
  a run); deep links to HF/OpenRouter; and a **Scout** button that screens a
  registered candidate on the discriminating subset. Live it surfaces
  `anthropic/claude-sonnet-5` (new *and* already carrying 1.6T tokens/30d) and 9
  gems nobody is serving.
- **The one-run-at-a-time lock was per-PROCESS, and that was a real bug.** Found
  by tripping it: a verify server on another port had its own `JobManager`, saw
  "idle", and started a scout run *while a run was executing on :8765* — the exact
  CPU contention that scored a correct 0.3s submission **0.0** in v0.5.9. It even
  wrote a result that would have silently superseded a real one as "latest".
  The lock now lives where every process can see it: `runner.active_run()` reads
  `runs/` for an unfinished manifest, and **`run_suite()` refuses** — the single
  choke point that the web panel, scout, and CLI all pass through. `--force`
  overrides.

### pricing & power

- **Local power cost.** The harness already sampled GPU energy every local run;
  it just never turned it into money, so a local model showed `$0.00` and the
  "local is free" assumption went unexamined. `directives.yaml` now takes a
  `power:` block (`cost_per_kwh`, `currency` — presentation, no version bump), and
  a **Power cost** column on the overview converts measured watt-hours at your
  rate. Live it spans **$0.004 (gpt-oss-20b, 25 Wh) to $0.13 (qwen3.6-27b, 851
  Wh)** for a full 39-task sweep — a 33x spread that was previously invisible.
  Stated honestly on /info: it is **GPU-only** (excludes CPU/system draw, PSU
  losses, cooling — a lower bound on the wall socket) and **marginal** (it ignores
  hardware amortisation entirely; the card dwarfs the electricity it will ever
  burn here). Use it to compare locals against each other — not to conclude
  "local wins", which omits the GPU's price tag.
- **A local model's cost IS its electricity now — everywhere.** The first cut
  added a Power-cost column but left `Cost / run` reading **$0** and `score/$`
  reading **"free"** on the leaderboard — i.e. it computed the honest number and
  then kept showing the dishonest one in the two places anyone actually looks.
  Local models now show their measured GPU electricity as their cost, marked ⚡,
  and are ranked on **score per dollar** instead of hiding behind "free".
  At $0.13/kWh: **gpt-oss-20b $0.0033 ⚡ → 8,792 score/$**, qwen3.6-27b $0.11 ⚡ →
  342, versus **claude-cli-opus $45.18 → 0.8**. That gap was completely invisible.
  Guardrail on /info: the comparison is **not symmetric** — a cloud price includes
  the provider's hardware and margin; the ⚡ figure includes none of yours (not the
  GPU, not the box). It is true as *marginal* cost and misleading as *total cost of
  ownership*. The local number is a floor; the cloud number is a price.
- **Set the electricity rate from the web UI** — an *Electricity rate* control on
  `/manage` (next to Rescore). It writes `directives.yaml` with targeted line
  edits so the file's comments survive, then re-renders the reports immediately.
  Presentation only: it never touches a score, so it's safe to change mid-run.

### harness only

- **Model watch (`harness watch`)** — polls the model world on demand and answers
  five questions without guessing: what's **NEW**, what's **HOT** (OpenRouter
  30-day token share — what people actually spend tokens on, not what got a press
  release), what's **FADING** (was carrying traffic, isn't now — this is how a
  model becomes irrelevant), what's **LOCAL-FIT** (a GGUF exists and it really
  fits the 32 GB card), and what's a **GEM** (trending on HuggingFace and *not
  served on OpenRouter at all* — hyped, unserved, untested).
  - HF's trending list is ~70% noise; we filter it on evidence, not name-guessing
    (`base_model:quantized/finetune` tags, `gguf` format repos, `pipeline_tag`,
    and a vendor-quant suffix backstop). Live: **100 raw → 28 original LLMs**.
  - VRAM fit uses the **real byte size** of the GGUF we'd load (shards summed)
    **plus the KV cache** — the half of the budget people forget. Ornith-1.0-9B is
    9.5 GB of weights and **4.3 GB of KV** at 32k. If config.json can't be read we
    report the fit as *unproven* rather than claiming it fits.
- **`harness scout <model>`** — screens a model on five deliberately
  discriminating tasks (chosen from the observed score spreads, covering all three
  lanes and both tiers) for ~1/8th the cost of a full run. The principle: never
  argue about a model from its spec sheet — **let the harness decide**.

## 0.5.11 — stop a model that thinks itself to death

`claude -p --output-format json` is **non-streaming**: it emits nothing until it
exits. So the harness was **blind** — it could not tell a model slowly but
genuinely producing an answer from one thinking itself to death, and paid the
**full budget either way, twice**, thanks to the retry.

claude-sonnet-4-6 sat on `web-002-maze` for **30+ minutes having emitted zero
assistant text**, while opus finished the same task in **208 seconds**. Under the
2400s budget that is **80 minutes of wall clock to produce a zero**.

- **The CLI now runs with `--output-format stream-json`** and the harness *watches
  it work*. A model emitting text gets its full budget. A model that has produced
  **nothing but thinking tokens** for `CLAUDE_SPIRAL_S` (default **300s**) is in a
  rumination spiral — a failure the suite already has a name for — and is stopped
  there, **non-retryable**, so it can't burn a second attempt.
  Verified live on the exact task that hung: **stopped at 301s instead of 30+
  minutes.** 80 min → 5 min.
- **All 34 task budgets CUT** (none raised), removing **~5 hours of worst-case wall
  time**. v0.5.10 had sized them on the pathological *maximum* — "the slowest run
  that happened to finish" — which is a rambler, not a requirement: web-002's
  median is **157s** and it had a **2400s** budget; ctx-008's median is 34s and it
  had 3600s. They are now sized to the slowest **genuine producer** (usually
  gemma-4-31b at 8 tok/s), which the spiral detector guarantees is the only thing
  that can consume them. web-002 2400→1500s, py-007 3600→1800s, ctx-008 3600→1800s.
  Verified: **no genuine success exceeds its tightened budget.**

### public-release scaffolding (Phase 1)

Groundwork for the staged open-source release: develop everything in this private
monorepo, publish an allowlisted PUBLIC SUBSET to a separate GitHub repo.

- **`tools/export_public.py`** — assembles the public tree from an explicit
  ALLOWLIST (a file is private unless named), then statically verifies the tree
  imports no private module before anything is pushed. Publishes the instrument
  (tasks, scoring, runner, report, the static site) + the run data as receipts;
  holds back the moat (watch), the operator control layer, studio/, and secrets.
- **Private CLI split** — the operator commands (watch / scout / rename-model /
  serve-control) moved to `harness/_control_cli.py`, loaded by `__main__.py` only
  when present. So the public `__main__` has no reference to a private module and
  the public CLI is exactly {add, list, run, report, rescore, archive, prune}.
- **`tests/test_boundary.py`** — fails if any public instrument module imports the
  operator layer. The seam was already clean; this keeps it that way.
- **`docs/PUBLIC-RELEASE.md`** — the boundary manifest and the release procedure.

Verified: export produces a verify-clean tree that imports and passes its 30
public tests standalone; the dev repo keeps all commands and 62/62 tests.
Phase 2 (next): extract a read-only `viewer` from review.py so `harness serve`
works in the public repo, plus a `public` nav mode with no dead control links.

## 0.5.10 — the time budget was only ever enforced on Claude

**A methodology change. Affected results must be re-run before they count.**

### The bug: `timeout_s` meant two different things

- **Streaming models (every local + API model):** the timeout was passed to
  `httpx.Timeout(timeout_s)`, which is a **per-read (inactivity)** timeout. While
  a model keeps emitting tokens it never fires — so a streaming model ran with
  **no total time limit at all.**
- **claude-cli:** `subprocess.run(timeout=timeout_s)` — a **hard total wall-clock
  kill.**

So the same number meant *"unbounded, as long as you keep talking"* for one group
and *"you die at T"* for the other. It is visible in the data:
**`gemma-4-31b` took 1125s on a 900s limit and scored 1.0**, while
**`claude-cli-sonnet` was killed at exactly 900s with zero output** on the same
task. Across the suite the limit was routinely blown by streaming models — a
`py-002` attempt ran **967s against a 180s limit**.

It is also why a Claude timeout yields *nothing*: the CLI returns its whole JSON
only at the end, so a kill discards 100% of the work.

**Fixed:** the streaming loop now enforces a **total-duration deadline**, so
`timeout_s` means the same thing for every provider.

### The budgets were never calibrated (because they were never enforced)

Since the limit never bound streaming models, the numbers in `meta.yaml` were
fiction. Enforcing them as-written would have retroactively failed models that
legitimately finished. So **28 task budgets were RAISED — none lowered** — sized
from the slowest *legitimate success* observed, with margin:

| | old | new |
|---|---|---|
| `py-007-regex-engine` | 300s | 3600s |
| `ctx-008-recall-128k` | 900s | 3600s |
| `py-004` / `py-005` | 300s | 2400s |
| `web-002-maze` | 900s | **2400s** |
| `web-006-spreadsheet` | 900s | 2400s |
| …24 more | | |

### The advisor didn't know about the clock

Enforcing the deadline created a **new failure mode**: until now, being slow was
free, so the /run advisor only predicted **VRAM and context** failures. It had no
concept of `timeout_s` — it would happily let you launch a run that burns hours to
produce a timeout.

`fit.timeout_risks()` now warns per model·task, grounded in the model's **own
slowest observed attempt** (real measurement, not a tok/s extrapolation — that
over-predicts badly, putting gemma-4-31b at 1850s on web-003 when it actually ran
well inside budget). It flags **before** the wall (>75% of budget) as well as at
it, and it covers **cloud models too** — the GGUF advisor only ever looked at
local ones, but a slow cloud model can now time out just the same.

Live, it catches exactly one: `glm-5.2` on `py-002-lru-cache`, whose slowest
attempt (967s) exceeds the new 600s budget. That attempt was a rumination spiral —
it hit the 32,768-token cap, emitted no code block, and failed on format, after
which attempt 2 succeeded in **12 seconds**. So enforcement *helps* here: it cuts
a doomed 16-minute ramble short without changing the score.

### The maze (v0.5's web-002 redesign) — the change that exposed all this

v0.5 replaced web-002 *"24 pathfinding bots"* with *"24 **EXPLORING** bots —
discovery, not omniscience"*: bots must explore, backtrack and remember dead
ends, and the checker states plainly that *"omniscient shortest-path walkers fail
here."* That is a substantially bigger program to write — **but its 900s budget
was never revisited.** Sonnet had already needed 421s / 36,207 tokens on the
*easier* v0.4 maze (vs opus 98s, haiku 136s); the harder task pushed it past the
wall, and it scored 0.0 having produced nothing. `hy3-free` blew it too.

Re-run required: results that hit the old ceiling — notably `claude-cli-sonnet`
and `hy3-free` on `web-002-maze` — are budget artifacts, not capability failures.

### coverage rule + content scaffolding

- **A model that hasn't attempted the whole suite is no longer ranked.** Found
  while wiring the content pipeline: `claude-cli-sonnet` sat at **#1 with 0.996
  over 25/39 tasks**, above a model scoring 0.969 over all 39 — because the 14
  tasks it never attempted (a subscription cap ate them) included ones it
  *demonstrably fails*. Its mean was inflated by its own absences, and the podium
  disclosed no task count at all. Incomplete models are now shown, labelled
  **partial**, and cannot take a podium place they haven't earned. Scores are
  unchanged; only the ranking and its disclosure.
- **`harness.report.leaderboard()`** is now the single canonical standings call,
  used by the overview page *and* the content pipeline. One aggregation, one
  ranking key — a video can never disagree with the site.
- **`studio/`** — the content pipeline, deliberately separate from the harness
  (own package, own CLI `python -m studio`, own launcher, own deps, gitignored
  `assets/`). It imports the harness read-only, never writes to `runs/`, never
  computes a score, and **refuses to do heavy work while a benchmark is
  executing** — because v0.5.9 proved CPU contention corrupts the very scores the
  run is measuring. Video capture is a separate pass over already-saved
  `app.html` files, so it can never influence a result.

## 0.5.9 — the timing budget was measuring the CPU, not the model

A full rescore of all 7 runs (796 results) changed only 9 — and those 9 exposed a
real methodology bug: **timing-sensitive checkers were load-dependent.**

The evidence was unambiguous. claude-haiku's saved `ag-006` workspace passes
**4/4 in 0.30 seconds** — three times running, a 6× margin inside the old 2s
budget. During the original run it scored **0.0**. Same code, same checker; the
only variable was machine load. Four models also silently lost `web-003-sand`
tests to the same cause (that checker is deterministic — 5/5 identical when idle).
An absolute wall-clock budget is an instrument calibrated to a machine, not to an
algorithm.

Worse, v0.5.6's no-op fix had *amplified* the blast radius: folding correctness
into each timing test (correctly, to kill the no-op floor) made correctness
**hostage to the clock** — haiku would have scored 0.5 under the old checker and
got 0.0 under the new one.

Fixes:
- **ag-006's budget is now calibrated.** Each timed subprocess first runs a fixed
  reference workload and measures how slow this box is *right now*, then scales
  its budget by that factor (capped). Under load the calibration and the workload
  slow down together, so the verdict is load-invariant. The base budget also
  widened 2s → 8s. Verified: the reference passes 4/4 even under 64 concurrent
  CPU hogs, while the naive O(n²) seed still fails every test. Discrimination is
  unchanged — rescoring moved no ag-006 score.
- **`harness rescore` now refuses to run while a run is executing.** Rescoring
  re-runs pytest timing budgets and headless Chromium; that contention steals the
  CPU those budgets are measured against. Skipping the in-flight run was not
  enough — the damage is to whatever the run is scoring *right now*. `--force` to
  override.

## 0.5.8 — info page, Claude cap handling, Windows-safe deletes

Presentation and run-engine only. **No test or scoring change**, so nothing was
archived and every `0.5.x` result stays directly comparable — results produced
under 0.5.7 and 0.5.8 are the same measurement.

- **New `/info` page** in the top nav — what the tests do, what the numbers mean,
  and this changelog. Categories, task counts, the 39-task catalog and the
  failure taxonomy all derive from the live task set and `assess.CATEGORIES`, so
  the page can't drift from the suite. Also documents run statuses, how to read
  each chart, the metrics glossary (wall *includes* retries; tries/pass;
  attributed score), the hardware fingerprint each run records — flagging when a
  dataset spans more than one rig, since speed figures then aren't comparable —
  where the raw data lives, and an honest **caveats** section (tier-2 Claude runs
  a different agent scaffold; OpenRouter host/quant drift; cost is an estimate;
  the answer lane is all-or-nothing; archived datasets predate the no-op-floor
  fixes).
- **Claude subscription caps handled cleanly.** Hitting a 5-hour / daily /
  weekly cap used to look like a generic retryable API error: the runner
  retried the wall, scored the task 0, and moved on to the next task — which
  hit the same cap — poisoning the leaderboard with fake zeros. The CLI adapter
  now detects the cap, drops the in-flight task **unscored** (a re-run after the
  reset fills the gap), skips that model's remaining tasks, and records the
  reset time. Non-Claude models queued in the same run keep going. The run is
  tagged **⏸ paused: usage limit** in the runs list.
- **Real cap wording detected.** The live message is
  `You've hit your session limit ∙ resets 2:50am (America/Chicago)` — the first
  cut only matched "usage limit reached" and missed it. Detection now covers
  "session limit" and carries Claude's human reset text through to the UI.
- **Deletion tolerates Windows file locks.** Deleting a run called a bare
  `shutil.rmtree`; a workspace still held by an exiting subprocess (`WinError
  32`) or a read-only file (`WinError 5`) crashed the HTTP handler thread and
  dumped a traceback to the console while the click did nothing. Now retries
  with backoff, clears read-only bits, and returns a clean "files are locked —
  try again in a moment" instead of crashing.
- **"files →" links restored in the run log.** The link's run id was scraped
  from the `run:` line, which scrolls out of the 200-line log window on any full
  run — so every completed task silently lost its link. The run id now comes
  from `/api/status`.
- **Serve banner prints the suite version.**

## 0.5.7 — answer-lane control-token fix

Cohere `north-mini-code` emitted **correct** answers with a trailing
`<|END_OF_TURN_TOKEN|>` that leaked into the response text. Neither the numeric
nor the exact matcher stripped it, so **15 genuinely-correct answers scored 0**
and the model's suite mean read **0.28 instead of 0.66**.

- `extract_answer` now strips chat-template control tokens (`<|…|>`, `</s>`,
  endoftext families) before matching. A suite-wide scan confirmed north was the
  only model leaking a token; rescoring the answer lane changed nothing else.
- **FORMAT-MISS guard** (future-proofing): any 0-scored answer whose expected
  value is present *inside the ANSWER line* is flagged
  `[FORMAT-MISS: …]`. It still scores 0 — we don't auto-parse unknown tokens —
  but it can no longer average in unnoticed. It inspects the ANSWER line only,
  so a value merely mentioned in reasoning is not a false positive.
- Regression tests: `tests/test_scoring.py`.

## 0.5.6 — ag-006 / ag-007 no-op floors removed

A suite-wide scan for models sharing an *identical partial score* found two more
"fix-it" tasks where an untouched seed collected free credit.

- **ag-007 (regression-hunt)** — 12 "load-bearing" guard tests passed on the
  seed, so a no-op floored at **12/15 = 0.80**, the worst floor in the suite (5
  models parked there). Redesigned to 3 tests, each asserting its target bug is
  fixed **and** all 12 guards are intact. No-op → 0.0, fix-2-of-3 → 0.667,
  breaking any guard → 0.0.
- **ag-006 (perf-optimize)** — 4 correctness tests passed on the correct-but-slow
  seed, flooring a no-op at **4/8 = 0.50**. Edge-case correctness folded into
  each timing test: one test per function, which must be **both correct and
  fast**. No-op → 0.0.
- **rescore bug fixed**: the `metrics.status == "ok"` gate silently skipped
  `max_turns` runs (whose workspaces were fully written and originally scored),
  leaving stale scores behind on *every* past rescore.

## 0.5.5 — ag-001 / ag-003 checker redesign

Both are "fix the bugs" tasks whose tests mostly exercised behavior that was
*already correct*, so a model that changed nothing near-passed: the untouched
seed scored **6/8 = 0.75** (ag-001) and **3/7 = 0.43** (ag-003). Redesigned so
nearly every test depends on a bug actually being fixed — no-op now scores 0.25
and 0.0, a real fix 1.0. Reference fixes live in `tasks-refs/`.

## 0.5.4 — retry loop honours `retryable`

The retry loop retried *every* error. Non-retryable ones (auth, HTTP 4xx,
context-window overflow, CLI misconfig) now fail fast instead of burning the
budget on backoff sleeps.

## 0.5.3 — web-002 maze autonomy + checker gaps

- **web-002** scored 1.0 on a *dead* maze — nothing verified the bots actually
  moved. Added an autonomy test.
- Hardened the forbidden-import bypass and added real DOM checks to **web-006**.

## 0.5.2 — rs-010 answer key fix

The ants-on-a-rod key was wrong (`75`; the correct value is `185/3 ≈ 61.67`).

## 0.5.1 — overview visual overhaul

Per-model summary pages, dots-only charts, clickable model names everywhere, a
wider layout, and total time / total tries on the leaderboard placards.
Presentation only — no scores changed.

## 0.5.0 — the v0.5 test suite

39 tasks (v0.4's 31, minus rs-007, plus 9 new). New rumination traps
(py-004/005/007/008), a 128k long-context task (ctx-008), agentic timing budgets
(ag-006), and a full exploration redesign of the web-002 maze. Every task
reference-verified: a known-good implementation must score 1.0 and an
empty/trap submission 0 before the task counts.

## 0.4.0 — initial

First tracked version of the benchmark suite: 31 tasks across five categories,
three scoring lanes, local (LM Studio) + cloud (Claude CLI, OpenRouter) models,
full timing/token/cost accounting, and regenerable HTML reports.
