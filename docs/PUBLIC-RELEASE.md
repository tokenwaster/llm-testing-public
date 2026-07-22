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
  registered models, some carry endpoint config), `watch/`, `scouts/`.
- **Strategy**: `docs/CONTENT-PLAN.md`.

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
