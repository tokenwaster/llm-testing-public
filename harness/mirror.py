"""The private held-out mirror: contamination measured instead of assumed.

Publishing the suite publishes the answers — a correct model reply recorded in
runs/ IS the key, so withholding tasks-refs or meta.yaml would not help and would
cost the auditability that makes the public data worth anything. The alternative
is to keep the public set fully open and hold back a PRIVATE variant of the same
task, regenerated at a different seed. A model that scores markedly higher on the
published instance than on the unpublished one has memorised the instance.

Only generated tasks can be mirrored: a task whose content comes from a seeded
generator can be re-rolled, while a hand-written app spec or agent workspace
cannot. mirrorable() reports exactly which, so the coverage claim stays honest.

What this does NOT detect: a model that learned the underlying skill from the
published task scores the same on both, and should — that is learning, not
cheating. The signal is verbatim memorisation only.
"""

import re
import shutil
from pathlib import Path

from . import config

_GEN = "generate.py"


class RunActive(RuntimeError):
    """A build was attempted while a run is executing — see build_mirror."""

_KEY_FILES = ("checker.py", "meta.yaml")


def _carries_key(pub_dir: Path, name: str) -> bool:
    """Does this file of the public task hold the expected answer?"""
    p = pub_dir / name
    if not p.is_file():
        return False
    if name == "checker.py":
        return True
    import yaml
    meta = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    scoring = meta.get("scoring") or {}
    return any(k in scoring for k in ("answer", "answers"))


def _stale_key(pub_dir: Path, regenerated: set[str]) -> str:
    """'' if the variant is scoreable, else why it is not."""
    missed = [n for n in _KEY_FILES
              if _carries_key(pub_dir, n) and n not in regenerated]
    if missed:
        return (f"the generator did not rewrite {', '.join(missed)}, so the "
                "variant would be graded against the PUBLIC answer key — every "
                "model would score 0 and read as contamination")
    return ""


def verify_variant(task) -> str:
    """'' if this private variant grades correctly, else why it does not.

    The same gate new public tasks pass (rule #5): a known-good submission must
    score 1.0 and an empty one 0.0. Applied to the mirror because a variant is
    generated code no human read — and a key that silently belongs to the public
    prompt fails exactly this check while looking fine on disk.

    The answer lane can be checked completely (its key is in meta.yaml, so the
    correct submission is constructible). A checker lane can only be checked from
    below — empty must earn nothing — because reconstructing a correct reply would
    mean reimplementing the checker.
    """
    from . import scoring
    if task.scoring_type == "answer":
        key = (task.scoring or {}).get("answer")
        if key is None:
            return "answer-lane variant with no answer in its meta.yaml"
        good = scoring.score_answer(task, f"Working it out.\nANSWER: {key}")
        if (good.get("score") or 0) < 1.0:
            return (f"the correct answer ({key!r}) scores "
                    f"{good.get('score')} against its own variant, not 1.0")
        if (scoring.score_answer(task, "").get("score") or 0) != 0.0:
            return "an empty submission scores above zero"
        return ""
    if task.checker:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            (ws / "response.txt").write_text("", encoding="utf-8")
            empty = scoring.run_pytest_checker(task, ws)
        if (empty.get("score") or 0) != 0.0:
            return (f"an empty submission scores {empty.get('score')} — the "
                    "checker awards credit for nothing")
    return ""


def produced_any(sandbox) -> bool:
    """Did the generator already write something? Running as __main__
    often does the work, in which case calling main() again would
    duplicate it."""
    return any(p.is_file() and p.name != _GEN
               for p in sandbox.rglob("*"))


def mirrorable() -> list[dict]:
    """Public tasks that can be re-seeded, with their generator + current seed."""
    from .tasks import load_tasks
    out = []
    for t in load_tasks():
        gen = config.ROOT / "tasks-refs" / t.id / _GEN
        if not gen.is_file():
            continue
        src = gen.read_text(encoding="utf-8")
        m = re.search(r"(?m)^SEED\s*=\s*(\d+)", src)
        out.append({"id": t.id, "category": t.category,
                    "seed": int(m.group(1)) if m else None,
                    "generator": str(gen.relative_to(config.ROOT))})
    return sorted(out, key=lambda x: x["id"])


def build_mirror(task_ids=None, seed_offset: int | None = None,
                 progress=print) -> list[str]:
    """Generate private variants of the given tasks at a shifted seed.

    Run in a SANDBOX, not in place. Generators resolve their output from
    `Path(__file__).resolve().parents[2]`, and some hardcode the destination
    inline rather than through a constant — rewriting an `OUT =` line therefore
    misses them and the generator writes straight into the PUBLIC task. That
    happened once here and overwrote tasks/long-context/ctx-013's prompt. So the
    generator is copied into a throwaway root whose parents[2] IS the sandbox,
    left free to write wherever it wants, and only the files it produced are
    harvested. The public task cannot be reached from there.

    Only SEED is rewritten. Everything else about the task — its shape, checker
    and answers format — must stay identical, or the two variants would not be
    comparable.

    A variant that the generator cannot fully re-key is REFUSED rather than
    shipped: see _stale_key. The reasons land in private/mirror.json so the
    operator page can state coverage from what was actually verified.
    """
    import tempfile
    from .util import now_iso, write_json
    from .runner import active_run
    busy = active_run()
    if busy:
        raise RunActive(
            f"run {busy} is executing — rebuilding the held-out variants now would "
            "rewrite the prompts it is reading. Wait for it to finish.")
    if seed_offset is None:
        seed_offset = config.mirror_seed_offset()
    avail = {t["id"]: t for t in mirrorable()}
    want = [t for t in (task_ids or list(avail)) if t in avail]
    built = []
    report: dict[str, dict] = {}
    for tid in want:
        info = avail[tid]
        gen = config.ROOT / info["generator"]
        pub = config.TASKS_DIR / info["category"] / tid
        out_dir = config.PRIVATE_TASKS_DIR / info["category"] / tid

        def _refuse(reason: str) -> None:
            """Never leave an unscoreable variant where a run could pick it up."""
            if out_dir.exists():
                shutil.rmtree(out_dir)
            report[tid] = {"category": info["category"], "ok": False,
                           "reason": reason, "generator": info["generator"],
                           "public_seed": info["seed"]}
            progress(f"  !! {tid}: {reason}")

        if info["seed"] is None:
            _refuse("no SEED constant to shift")
            continue
        new_seed = info["seed"] + seed_offset
        src = re.sub(r"(?m)^SEED\s*=\s*\d+", lambda _: f"SEED = {new_seed}",
                     gen.read_text(encoding="utf-8"), count=1)
        with tempfile.TemporaryDirectory(prefix="mirror-") as td:
            sandbox = Path(td)
            gdir = sandbox / "tasks-refs" / tid
            gdir.mkdir(parents=True)
            for sub in ("tasks", "tasks-staging"):
                (sandbox / sub / info["category"] / tid).mkdir(parents=True,
                                                               exist_ok=True)
            (gdir / _GEN).write_text(src, encoding="utf-8")
            ns = {"__name__": "__main__", "__file__": str(gdir / _GEN)}
            exec(compile(src, str(gdir / _GEN), "exec"), ns)
            if callable(ns.get("main")) and not produced_any(sandbox):
                ns["main"]()
            produced = [p for p in sandbox.rglob("*")
                        if p.is_file() and p.name != _GEN]
            if not produced:
                _refuse("generator produced nothing in the sandbox")
                continue
            regenerated = {p.name for p in produced}
            by_name = {p.name: p for p in produced}
            reason = _stale_key(pub, regenerated)
            if not reason:
                for name in ("prompt.md", *_KEY_FILES):
                    src, dst = pub / name, by_name.get(name)
                    if src.is_file() and dst is not None \
                            and src.read_bytes() == dst.read_bytes() \
                            and (name == "prompt.md" or _carries_key(pub, name)):
                        reason = (f"the re-seeded {name} is byte-identical to the "
                                  "public one, so the variant measures nothing")
                        break
            if reason:
                _refuse(reason)
                continue
            if out_dir.exists():
                shutil.rmtree(out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            if pub.is_dir():
                shutil.copytree(pub, out_dir, dirs_exist_ok=True)
            for f in produced:
                shutil.copy2(f, out_dir / f.name)
        (out_dir / "MIRROR.txt").write_text(
            "\n".join([
                f"private held-out variant of {tid}",
                f"generator: {info['generator']}",
                f"public seed: {info['seed']}",
                f"private seed: {new_seed}",
                "never published: private/ is gitignored and absent from the "
                "export allowlist",
            ]) + "\n", encoding="utf-8")
        from .tasks import _load_task
        reason = verify_variant(_load_task(out_dir, info["category"]))
        if reason:
            _refuse(reason)
            continue
        report[tid] = {"category": info["category"], "ok": True,
                       "generator": info["generator"],
                       "public_seed": info["seed"], "private_seed": new_seed,
                       "regenerated": sorted(regenerated)}
        built.append(tid)
        progress(f"  + {tid}  (seed {info['seed']} -> {new_seed}, "
                 f"re-keyed {', '.join(sorted(regenerated))}, verified)")
    prev = _load_report().get("tasks") or {}
    prev.update(report)
    config.PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(config.PRIVATE_DIR / "mirror.json",
               {"built_at": now_iso(), "seed_offset": seed_offset,
                "tasks": prev})
    return built


def _load_report() -> dict:
    from .util import read_json
    return read_json(config.PRIVATE_DIR / "mirror.json", {})


def load_private_tasks():
    """The mirror's tasks, loaded with the same loader as the public suite."""
    from .tasks import load_tasks
    if not config.PRIVATE_TASKS_DIR.is_dir():
        return []
    return load_tasks(config.PRIVATE_TASKS_DIR)


def delta_band(delta: float, n: int) -> str:
    """'flat' | 'watch' | 'suspect' for a public-vs-private delta over n tasks.

    Scaled by n, not a fixed number. One task flipping 1.0 -> 0.0 moves the mean
    by exactly 1/n, so a constant threshold means something different at every
    coverage level: 0.15 was chosen first and happens to sit below 1/6 = 0.167,
    which made a SINGLE differing task read as a finding. The bands are therefore
    stated in units of "tasks' worth of difference":

      flat    <= one task's worth   — expected; re-seeding is not difficulty-neutral
      watch   <= two tasks' worth
      suspect  > two tasks' worth

    Negative is always flat: memorising the published instance can only inflate the
    PUBLIC side, so a better private score is noise, not virtue.
    """
    if n <= 0 or delta <= 1.0 / n:
        return "flat"
    return "watch" if delta <= 2.0 / n else "suspect"


def built_ids() -> set[str]:
    """Task ids with a variant actually on disk — the only ones that can be run
    or compared. mirrorable() says what COULD be mirrored; this says what is."""
    return {t.id for t in load_private_tasks()}


def private_scores() -> dict[tuple, list[float]]:
    """{(model, task): [scores]} from private/runs — never the public aggregate."""
    from .util import read_json
    out: dict[tuple, list[float]] = {}
    if not config.PRIVATE_RUNS_DIR.is_dir():
        return out
    for mfile in sorted(config.PRIVATE_RUNS_DIR.glob("*/*/*/metrics.json")):
        sc = read_json(mfile.parent / "score.json", {})
        if sc.get("status") == "scored" and sc.get("score") is not None:
            out.setdefault((mfile.parents[1].name, mfile.parent.name),
                           []).append(sc["score"])
    return out


def contamination_delta(pub: dict | None = None) -> list[dict]:
    """Per model: public score vs private score on the mirrored tasks.

    A positive delta means the model did BETTER on the published instance than on
    an unpublished one of the same shape — the signature of having memorised it.
    Reported per model with n, so a one-task difference is not read as a finding.

    Both sides use the suite's aggregation basis: every scored run of that
    model·task, meaned. The public side comes from report.collect_task_data (the
    same numbers the leaderboard shows), so the two columns are comparable. Pass
    `pub` when the caller already has that data — the report render does, and
    reloading every run to build it again is the expensive part.
    """
    mirrored = built_ids()
    priv = {k: v for k, v in private_scores().items() if k[1] in mirrored}
    if not mirrored or not priv:
        return []
    if pub is None:
        from .report import collect_task_data, load_all_runs
        pub = collect_task_data(load_all_runs())
    rows = []
    for model in sorted({m for m, _ in priv}):
        pairs = []
        for tid in sorted(mirrored):
            pv = priv.get((model, tid))
            agg = (pub.get(tid) or {}).get("agg", {}).get(model)
            if not pv or not agg:
                continue
            s = agg["score"]
            if s.get("status") != "scored" or s.get("score") is None:
                continue
            pairs.append({"task": tid, "public": round(s["score"], 3),
                          "private": round(sum(pv) / len(pv), 3),
                          "n_private": len(pv),
                          "n_public": agg.get("n_scored") or 1})
        if not pairs:
            continue
        pub_mean = sum(p["public"] for p in pairs) / len(pairs)
        prv_mean = sum(p["private"] for p in pairs) / len(pairs)
        d = pub_mean - prv_mean
        rows.append({"model": model, "n": len(pairs),
                     "public": round(pub_mean, 3), "private": round(prv_mean, 3),
                     "delta": round(d, 3),
                     "band": delta_band(d, len(pairs)),
                     "one_task": round(1.0 / len(pairs), 3),
                     "tasks": [p["task"] for p in pairs],
                     "pairs": pairs})
    rows.sort(key=lambda r: -r["delta"])
    return rows


def mirror_state(pub: dict | None = None, with_delta: bool = True) -> dict:
    """Everything the operator page and the report pages need, from disk.

    Coverage is stated as a fraction of the WHOLE public suite, including the
    tasks that can never be mirrored, because "6 of 6 built" would read as full
    coverage when it is 6 of 55. Held-out coverage that overstates itself is
    worse than none.

    `with_delta=False` skips the public/private comparison, which is the only
    costly part — it reloads every run to rebuild the public aggregate (measured
    0.4s across this dataset, and it grows with runs/). The control page drops it
    while a run executes: the page polls, and re-reading every run every few
    seconds is disk and CPU that the timing-scored tasks calibrate against an idle
    machine to earn.
    """
    from .tasks import load_tasks
    pub_tasks = load_tasks()
    can = {t["id"]: t for t in mirrorable()}
    have = built_ids()
    rep = _load_report()
    reasons = rep.get("tasks") or {}
    priv = private_scores()
    covered = {t for _, t in priv}

    rows = []
    for tid, info in can.items():
        r = reasons.get(tid) or {}
        pdir = config.PRIVATE_TASKS_DIR / info["category"] / tid
        rows.append({
            "id": tid, "category": info["category"],
            "generator": info["generator"],
            "public_seed": info["seed"],
            "built": tid in have,
            "regenerated": r.get("regenerated") or [],
            "blocked": (r.get("reason") or "") if not r.get("ok", True) else "",
            "private_bytes": ((pdir / "prompt.md").stat().st_size
                              if (pdir / "prompt.md").is_file() else None),
            "public_bytes": (config.TASKS_DIR / info["category"] / tid
                             / "prompt.md").stat().st_size,
            "models_run": sorted(m for m, t in priv if t == tid),
        })
    rows.sort(key=lambda r: r["id"])

    not_mirrorable: dict[str, int] = {}
    for t in pub_tasks:
        if t.id not in can:
            not_mirrorable[t.category] = not_mirrorable.get(t.category, 0) + 1

    runs = []
    if config.PRIVATE_RUNS_DIR.is_dir():
        from .util import read_json
        for rj in sorted(config.PRIVATE_RUNS_DIR.glob("*/run.json"), reverse=True):
            m = read_json(rj, {})
            runs.append({"id": rj.parent.name, "tag": m.get("tag", ""),
                         "started": m.get("started", ""),
                         "finished": m.get("finished"),
                         "models": m.get("models") or [],
                         "n_tasks": len(m.get("tasks") or [])})
    return {
        "tasks": rows,
        "n_public": len(pub_tasks),
        "n_mirrorable": len(can),
        "n_built": len(have & set(can)),
        "n_blocked": sum(1 for r in rows if r["blocked"]),
        "n_measured": len(covered & have),
        "not_mirrorable": sorted(not_mirrorable.items()),
        "built_at": rep.get("built_at"),
        "runs": runs,
        "delta": contamination_delta(pub) if with_delta else [],
    }
