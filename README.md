# LLM Testing Suite

A published benchmark of large language models — local models (LM Studio, Ollama,
any OpenAI-compatible server) alongside cloud APIs (Anthropic, OpenAI,
OpenRouter) — scored on 52 tasks with full timing, token, retry and cost
accounting.

**This repo ships the results *and* the receipts.** Every number on the generated
site is backed by the run data in `runs/` and `archive/`: complete transcripts,
per-request metrics, scores, and the model's own workspace files exactly as it
left them. Nothing is summarised away, so any figure can be traced back to the
request that produced it.

## Browsing the results

Create a virtualenv, install the requirements, then run `serve` — three lines,
below. `serve` opens the results site at http://127.0.0.1:9001 as a read-only
viewer bound to localhost, and is the only command you need for every run after
setup.

**Windows** — works as written in both PowerShell and `cmd`:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m harness serve
```

**Linux and macOS** — identical on both:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m harness serve
```

Calling the venv's interpreter by path means there is nothing to activate, so
the two blocks above are the whole story — no per-shell activation script and no
PowerShell execution-policy exemption. `.\harness.ps1 serve` is a shorter
equivalent on Windows, but it is PowerShell-only, and Windows blocks `.ps1`
files under the default RemoteSigned policy if you unpacked a downloaded ZIP
rather than cloning.

Python 3.11+ is required. Add `--port N` to serve somewhere else.

Or skip Python entirely — `reports/` is self-contained static HTML, so opening
`reports/index.html` in a browser works with no install and no server, as does
hosting the folder anywhere.

- `index.html` — leaderboard, the model × task matrix (filterable to All / Hard /
  Easy), score trends, speed and cost, and per-category task fit
- `tasks/<id>.html` — one task across every model: ranked comparison plus each
  model's verbatim output side by side
- `models/<name>.html` — one model's per-task detail and its run-over-run matrix
- `discriminate.html` — which tasks actually separate models, and who wins the
  ones that do
- `info.html` — what everything means: scoring lanes, tiers, the metrics
  glossary, the failure taxonomy, pricing caveats, and the changelog
- `data/…` — a read-only browser over the raw `runs/` tree

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

- **Tier 1** — single-shot: one prompt in, one response out. Every model runs these.
- **Tier 2** — agentic: the model gets `list_files` / `read_file` / `write_file` /
  `run_python` in a private workspace and iterates. Models without tool support
  skip these.

Every task is a brand-new conversation — exactly one user message (plus tool
round-trips inside a tier-2 task), never anything carried over from a previous
task. Transcripts record `n_messages` and `roles` per request, so this is
auditable rather than asserted.

## Methodology guarantees

- Every result stores a **content hash of the task definition**. If a task is
  edited, the report flags the break instead of silently mixing versions.
- A model's score for a task is the **mean of every scored run** of it, not the
  latest — re-testing fleshes the number out rather than replacing it. Unscored
  runs (crash, spiral, DNF) stay out of the mean.
- `runs/` is append-only ground truth. `reports/` is a pure function of it.
- Cost is the gateway's **actual billed amount** where the provider reports one,
  otherwise computed from list price. Local models are costed by measured GPU
  electricity. See the Pricing section of `info.html` for the caveats, including
  why a promotional `:free` price is never treated as durable.
- Every model gets the same prompts, the same task versions, the same token
  budget, and its own isolated workspace. Runs are sequential so local GPU
  timing is honest.

Failing is fine — the hard tasks exist so models have headroom. A model that
solves 64k-token recall tells you more than ten models tied at 1.00 on easy ones.

## Versioned datasets

`SUITE_VERSION` is stamped into every run manifest. Patch bumps are fixes with no
methodology change; minor and major bumps mean the tests themselves changed, so
the previous data is archived first and the live report always shows exactly one
coherent dataset. Archived sets are under `archive/` and render as their own
sites at `reports/datasets/`.

## How a task is built

Each task is a directory under `tasks/<category>/<task-id>/`:

- `prompt.md` — what the model is asked
- `meta.yaml` — id, tier, scoring lane, timeouts
- `checker.py` — the grader, for the pytest / webapp / response lanes
- `setup/` — optional files pre-seeded into a tier-2 workspace

A task counts only once a known-good reference solution scores 1.0 **and** an
empty or trap submission scores ~0 — otherwise the task is measuring nothing.
Reference solutions and generators live in `tasks-refs/`.

## Layout

```
tasks/      task definitions, content-hashed into every result
tasks-refs/ reference solutions used to validate that each task discriminates
runs/       append-only results: transcripts, metrics, scores, workspaces
archive/    previous dataset versions, frozen
reports/    the generated site
harness/    the instrument that produced the data
tests/      the harness's own test suite
```

## About this repo

The suite is developed in a private monorepo; this is an allowlisted export of
the published results and the instrument that produced them. The operator layer —
the run and management control panel, the model-discovery pipeline, and the
content pipeline — is not part of this repo.

## License

MIT — see `LICENSE`.
