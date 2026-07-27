# Public release — the boundary

We develop everything in one private repo and **export an allowlisted subset** to
a separate public GitHub repo. The export is a *whitelist*: a new file is private
by default and only becomes public if it's deliberately added to the allowlist.
A leak therefore requires a mistake of commission, never one of omission.

## What's public — the instrument + the receipts

The public repo is a **reproducible benchmark harness**: clone it, add your own
models with your own keys, run the same tasks, get comparable numbers. That
reproducibility is the whole credibility play — the community trusts a public
harness, not a results website.

- **`harness/`** — but only the instrument modules (see the allowlist in
  `tools/export_public.py`): config, util, registry, tasks, adapters, scoring,
  runner, telemetry, tools, lmstudio, gguf, report, fit, archive, assess,
  rescore, discover, interfaces, and the read-only `viewer`.
- **`tasks/`, `tasks-refs/`** — the test definitions and their reference
  solutions. This is the methodology, in the open.
- **`harness/mirror.py`** — how contamination is measured (see below). The
  *method* is public; the held-out instances are not.
- **`tests/`** — the harness's own test suite.
- **`runs/`, `archive/`** — the actual run data. The receipts. A leaderboard
  backed by inspectable transcripts is the strongest trust signal we have.
- **`reports/`** — the generated static site (also deployable to GitHub Pages).
- **README.md, CHANGELOG.md, requirements.txt**, methodology docs.

## What's private — the operator layer, the moat, the secrets

Never in the public repo:

- **`harness/watch.py`** — the model-discovery pipeline. This is the competitive
  moat: "the harness decides what's worth testing." Kept private on purpose.
- **`harness/jobs.py`, the control endpoints of `harness/review.py`** — the run
  control panel, /manage (data deletion/rescore), /backend (interface + key
  management). Operational, and a public-deployed control surface could spend
  your subscription or mutate your data.
- **`harness/scout.py`, `harness/rename.py`** — triage + data-maintenance ops.
- **`studio/`** — the content pipeline: channel strategy, drafts, and (later)
  OAuth tokens.
- **Secrets & operator state**: `.env`, `interfaces.yaml`, `models/` (your
  registered models, some carry endpoint config), `watch/`, `scouts/`,
  `settings.local.json`.
- **`private/`** — the held-out mirror: the re-seeded task variants and their run
  data. Publishing these would defeat the only thing they exist to do.
- **Strategy**: `docs/CONTENT-PLAN.md`.

## Contamination — the held-out mirror

Publishing the suite publishes the answers. Not in a key file: **a correct model
reply recorded in `runs/` *is* the answer key**, and `runs/` is exactly what we
publish so the numbers can be audited. So every public task decays once it's
indexed — a later model can score well by having seen the instance rather than by
having the skill. Withholding the tasks would fix that and destroy the
auditability that makes the data worth anything.

So the public set stays fully open, and a **private variant of the same task** is
held back: same generator, re-run at a **different seed**, never published. A model
that scores markedly higher on the published instance than on the unpublished one
has memorised *that instance*.

**What ships and what doesn't:**

- **Public**: `harness/mirror.py` (the whole method — how variants are built,
  verified, and compared), and the *result* — the per-model public-vs-private table
  in the info page's Contamination section plus a *Held-out mirror* row on each
  model page.
- **Private**: `private/tasks/` (the variants), `private/runs/` (their results),
  and **the seed offset**. The offset is not a constant anywhere in the shipped
  code — `config.mirror_seed_offset()` reads it from `MIRROR_SEED_OFFSET` or
  `settings.local.json`, and mints one per operator if absent. It has to be secret
  because `tasks-refs/` *is* published and the generators are deterministic in
  their seed: a published offset is a complete recipe for regenerating the held-out
  set. Publish the method, keep the key.

**Honest limits, stated on the site as well as here:**

- **Coverage is partial.** Only tasks whose content comes from a seeded generator
  can be re-rolled. Hand-written app specs, agent workspaces and fixed prompts
  cannot, so the check is *silent* about them — the info page states the fraction
  rather than implying whole-suite coverage.
- **Private results never enter the public aggregate.** A variant carries the
  *same task id* as its public counterpart, so a private result in `runs/` would be
  indistinguishable from a public one and would average a held-out score into the
  published cell. Two trees, permanently; every aggregation path reads `runs/`
  only. The published score is unaffected by whether the mirror was ever run.
- **Re-seeding is not difficulty-neutral.** A re-rolled instance can be genuinely
  easier or harder, so a small delta is instance noise, not evidence. The verdict
  is therefore sized against the number of paired tasks — one task differing moves
  the mean by `1/n` — instead of a fixed cutoff.
- **It detects memorisation of the published instance, nothing more.** A model that
  genuinely learned the skill scores the same on both, and should. That's learning,
  not cheating, and the delta is built to read it that way.
- **A held-out set is not externally verifiable**, by construction. You can audit
  how it is measured; you cannot re-run it. That is the cost of the only design
  that keeps the public set open.

**A variant only counts if it grades itself.** The build refuses any variant whose
answer key the generator didn't rewrite — or rewrote to identical bytes — and
requires a correct submission to score 1.0 and an empty one 0.0 before admitting
it. This is the same gate new public tasks pass, and it exists because it caught a
real failure: a generator that wrote a fresh prompt but left the answer key from
the published instance, which would have scored every model 0 and read as total
contamination.

## The one rule, enforced in code

**The public instrument never imports a private module.** `harness/` public
modules must not `import` watch / jobs / review / scout / rename / studio.
`tests/test_boundary.py` fails the build if they do. (The reverse is fine and
expected: the private layer imports the public instrument freely.)

## How a release happens

```
python tools/export_public.py            # dry run: shows exactly what ships
python tools/export_public.py --out dist/public --verify
```

The script copies the allowlist into a clean tree, then **statically checks that
nothing in it imports a private module** — so an accidental dependency is caught
before anything is pushed. Publishing the tree to the public remote is a manual,
human step (never automated).

## `harness serve` across the boundary

`serve` is defined once, in the public `__main__.py`, and dispatches to the
**read-only `harness/viewer.py`** — static pages, the dataset switcher
(`/api/versions`), and read-only browsing of `runs/`. No control routes, no
POST: a publicly-deployed instance can't spend a subscription or mutate data.
Nav links to the operator pages (`/run`, `/watch`, `/backend`, `/manage`)
resolve to a short "operator-only" stub rather than a dead 404.

On the operator's machine, `_control_cli.py` is present and **overrides the
`serve` handler** with the full control server (`review.serve`), adding the
`review` alias. In the public export `_control_cli` is absent, so `serve` stays
the viewer. Same command, two servers, decided entirely by which files shipped.

## Publishing — one command, three enforced rules

The private monorepo and the public repo are **two separate git repositories
that never share history**. `harness/publish.py` (private) exports, verifies,
commits and optionally pushes from `dist/public`, which is its own repo:

```
harness publish -m "message"           # export + verify + commit locally
harness publish -m "message" --push    # ...and push to origin
```

Also on **/manage → Publish to GitHub** (operator-only; `harness/publish.py` is
in `PRIVATE_HARNESS`, so a public deployment has no publish route at all).

Three rules are enforced in code, not by discipline:

1. **Private history can never travel.** `dist/public` is `git init`-ed fresh;
   publishing refuses if the private repo is ever a remote of it.
2. **No AI co-authorship trailers in public commits.** Every commit in the
   private repo carries one; the publisher rejects a message containing one.
3. **Identity is set repo-locally** (`tokenwaster <tokenwaster@gmail.com>`), so a
   second GitHub account on the same machine cannot sign these commits.

Plus a final guard on the actual bytes before any commit: refuse if `.env`,
`interfaces.yaml`, `studio/`, `watch/`, `scouts/` or any private harness module
is present in the tree.

**Auth** is never handled by the harness. The remote is an SSH alias
(`git@github-tokenwaster:...`) so the second account's key is used without
colliding with the primary account's credentials. A push that isn't configured
fails with git's own message.

`dist/` is gitignored in the private repo — the public working copy must never
be tracked here.

## Phase status

- **Phase 1 (done):** boundary manifest, allowlist export + import check,
  boundary test.
- **Phase 2 (done):** read-only `harness/viewer.py` extracted; public
  `harness serve` runs the viewer, operator `serve` runs the control panel via
  the handler override. Control-nav links degrade to an operator-only stub.
- **Phase 3 (done):** export made green — `prices.py` added to the allowlist,
  private-module tests held back, `hardened_completion` moved to public
  `config.py` so its test ships, `_example-*.yaml` model templates ship, MIT
  LICENSE added. **The verify is now AST-based** and walks nested/function-level
  imports: a regex once passed a tree whose test imported `harness.review`
  inside a function body, and the fresh clone still broke. Acceptance gate is
  the exported tree's own suite: **167 passed**.
- **Phase 4 (done):** `harness publish` + /manage button, with the three rules
  above enforced in code.
