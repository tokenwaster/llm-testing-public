# LLM Testing Suite

A reproducible benchmark harness for comparing LLMs — local (LM Studio, Ollama,
any OpenAI-compatible server) against cloud APIs (Anthropic, OpenAI, OpenRouter)
— with full timing, token, retry and cost accounting, and HTML reports that stay
comparable over time.

**This repo ships the instrument *and* the receipts.** Every number on the
generated site is backed by the actual run data in `runs/` and `archive/` —
full transcripts, metrics, scores, and the model's own workspace files. Clone
it, point it at your own models with your own keys, and reproduce the numbers.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\harness.ps1 add lmstudio       # auto-register every model LM Studio is serving
.\harness.ps1 run                # run all enabled models x all tasks
.\harness.ps1 serve              # results site at http://127.0.0.1:8765
```

On Linux/macOS use `.venv/bin/python -m harness ...` in place of
`.\harness.ps1 ...`. Run `harness --help` for the full command list.

## Registering models

**Automatic:**

```powershell
.\harness.ps1 add lmstudio       # everything the LM Studio server offers
.\harness.ps1 add claude sonnet  # Claude via the Claude Code CLI subscription
```

**Manual:** copy a `models/_example-*.yaml` template (drop the leading
underscore) for Anthropic, OpenAI, OpenRouter, Groq, or any OpenAI-compatible
endpoint, then set its `key_env` and `base_url`. API keys live in a gitignored
`.env` at the project root; real environment variables win over it.

`add` writes one yaml per model and never overwrites an existing file — edit it
afterwards to tweak `max_tokens`, `pricing`, or `supports_tools`.

## Running

```powershell
.\harness.ps1 run                      # all models x all tasks
.\harness.ps1 run --models my-model    # one model
.\harness.ps1 run --tasks "py-*"       # subset (glob on task id or category)
.\harness.ps1 run --tier 1             # skip agentic tasks
.\harness.ps1 run --repeat 3           # N trials, for a variance/consistency read
```

Runs are sequential by default so local GPU timing is honest. Folders under
`runs/` are created automatically — never make them by hand. Every model gets
the same prompts, the same task versions, and its own isolated workspace.

## Viewing the results

```powershell
.\harness.ps1 serve                    # http://127.0.0.1:8765
```

`serve` is a **read-only viewer**: the results site with no run controls and no
LM Studio access, bound to localhost. Pages:

- `/` — leaderboard, the model x task matrix (filterable to All / Hard / Easy),
  score trends, speed and cost, and per-category task fit
- `/tasks/<id>.html` — one task across every model: ranked comparison plus each
  model's verbatim output side by side
- `/models/<name>.html` — one model's per-task detail and run-over-run matrix
- `/discriminate.html` — which tasks actually separate models, and who is best
  on the ones that do
- `/info.html` — what everything means: scoring lanes, tiers, the metrics
  glossary, the failure taxonomy, pricing caveats, and the changelog
- `/data/…` — read-only browser over `runs/`

`reports/` is plain self-contained HTML — host it anywhere (including GitHub
Pages) with no server or Python needed.

## The task suite

52 tasks across 10 categories (`SUITE_VERSION` 0.6.x):

| Category | Tasks | Lane | What it measures |
|---|---|---|---|
| agentic | 8 | pytest | multi-file navigation, self-verification, tool use in a real workspace |
| one-shot-apps | 12 | webapp | large coherent one-shot builds, driven by headless Chromium |
| long-context | 10 | answer | precision retrieval, recency, whole-window aggregation under distractors |
| coding-python | 6 | pytest | parsing, edge-case discipline, algorithmic correctness |
| reasoning | 6 | answer | deduction and twisted classics that punish memorized answers |
| instruction-following | 2 | response | obeying precise output constraints |
| hallucination | 2 | response | grounded QA — abstaining instead of inventing |
| extraction | 2 | response | messy text into strict, normalized JSON |
| math | 2 | answer | multi-step numeric word problems |
| tool-use | 2 | response | choosing the right tool call, and declining when args are missing |

### Scoring lanes

| Lane | Mechanism |
|---|---|
| `pytest` | a checker test-suite runs against the model's workspace; score = pass rate |
| `answer` | the final `ANSWER:` line is matched (exact / numeric / regex) |
| `webapp` | the model emits one self-contained `app.html`; a Playwright suite clicks, types and reloads it and asserts real behavior |
| `response` | the raw reply is inspected directly — format constraints, JSON field accuracy, grounded-answer vs abstention |

### Tiers

- **Tier 1** — single-shot: one prompt in, one response out. Every model can run these.
- **Tier 2** — agentic: the model gets `list_files` / `read_file` / `write_file` /
  `run_python` in a private workspace and iterates. Models with
  `supports_tools: false` skip these automatically.

Every task is a brand-new conversation — exactly one user message (plus tool
round-trips inside a tier-2 task), never anything carried from a previous task.
Transcripts record `n_messages` and `roles` per request so this is auditable
rather than asserted.

## Methodology guarantees

- Every result stores a **content hash of the task definition**. Edit a task and
  the report flags the break instead of silently mixing versions.
- A model's score for a task is the **mean of every scored run** of it, not the
  latest — re-testing fleshes the number out rather than replacing it. Unscored
  runs (crash, spiral, DNF) stay out of the mean.
- `runs/` is append-only ground truth. `reports/` is a pure function of it —
  delete and regenerate any time with `harness report`.
- Cost is the gateway's **actual billed amount** where the provider reports one,
  otherwise computed from the model yaml's list price. Local models are costed
  by measured GPU electricity. See the Pricing section of `/info.html` for the
  caveats, including why a promotional `:free` price is never treated as durable.

Failing is fine — the hard tasks exist so models have headroom. A model that
solves 64k-token recall tells you more than ten models tied at 1.00 on easy ones.

## Versioned datasets

`SUITE_VERSION` is stamped into every run manifest. Patch bumps are fixes with
no methodology change; minor/major bumps mean the tests changed, so the old data
is archived first and live reports always show exactly one coherent dataset.

```powershell
.\harness.ps1 archive --list          # what's archived
.\harness.ps1 report --dataset 0.5    # render an archived set
```

## Adding a task

Create `tasks/<category>/<task-id>/` with:

- `prompt.md` — what the model is asked
- `meta.yaml` — id, tier, `scoring:` (`pytest` | `answer` | `webapp` | `response`), timeouts
- `checker.py` — for the pytest/webapp/response lanes
- `setup/` — optional files pre-seeded into a tier-2 workspace

A new task ships only once a known-good reference solution scores 1.0 and an
empty or trap submission scores ~0 — otherwise the task is measuring nothing.

## Layout

```
harness/    runner, adapters, scoring lanes, report generation, read-only viewer
models/     one yaml per model (_example-*.yaml are templates)
tasks/      task definitions, content-hashed into every result
runs/       append-only results: transcripts, metrics, scores, workspaces
reports/    generated HTML, regenerable at any time
```

## About this repo

The suite is developed in a private monorepo; this public repo is an
**allowlisted export** of the instrument plus the run data. The operator layer —
the run/manage control panel, the model-discovery pipeline, and the content
pipeline — stays private, so a cloned or hosted instance can never spend a
subscription or mutate data. `harness --help` here lists exactly the commands
that ship. See `docs/PUBLIC-RELEASE.md` for the boundary.

## License

MIT — see `LICENSE`.
