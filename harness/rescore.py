"""Re-grade saved results without any model calls — used by the CLI
(`harness rescore`) and the web control panel (/run and /manage).

Covers all automatic lanes:
  - pytest / webapp: re-run the checker against the saved workspace
  - answer: re-match the saved transcript's ANSWER line against the CURRENT
    meta (so a corrected answer key or tolerance re-scores for free)

The currently-executing run (run.json finished == null) is SKIPPED — its
results are mid-write, and re-scoring them would race the live run. This
makes rescore safe to trigger even while a run is active elsewhere.
"""

import fnmatch

from . import config, report, scoring
from .tasks import load_tasks
from .util import read_json, read_jsonl, write_json


def rescore(selector="*", progress=print, force: bool = False) -> int:
    from .util import keep_awake
    with keep_awake():
        return _rescore(selector, progress, force=force)


def _matches(task_id: str, selector) -> bool:
    """selector: a list/set of exact task ids, or an fnmatch glob string."""
    if isinstance(selector, (list, set, tuple)):
        return task_id in selector
    return fnmatch.fnmatch(task_id, selector)


def _final_response(tdir) -> str | None:
    """Last model response text from the transcript (what the answer lane
    graded at run time)."""
    lines = read_jsonl(tdir / "transcript.jsonl")
    text = None
    for d in lines:
        if d.get("event") == "response" and d.get("text") is not None:
            text = d["text"]
    return text


class RunInProgress(Exception):
    """A run is executing — rescoring now would corrupt its timings."""


def _active_run() -> str | None:
    for run_dir in sorted(p for p in config.RUNS_DIR.iterdir() if p.is_dir()):
        manifest = read_json(run_dir / "run.json", {})
        if manifest and not manifest.get("finished"):
            return run_dir.name
    return None


def _rescore(selector, progress=print, force: bool = False) -> int:
    active = _active_run()
    if active and not force:
        raise RunInProgress(
            f"run {active} is still executing. Rescoring competes for the CPU "
            "that timing-sensitive checkers (ag-006, the webapp lane) measure "
            "against, which can wrongly zero a correct submission. Wait for the "
            "run to finish, or pass --force if you accept that risk.")

    tasks = {t.id: t for t in load_tasks()}
    n = 0
    skipped_human: list[str] = []
    for run_dir in sorted(p for p in config.RUNS_DIR.iterdir() if p.is_dir()):
        manifest = read_json(run_dir / "run.json", {})
        if manifest and not manifest.get("finished"):
            progress(f"{run_dir.name}: still running — skipped")
            continue
        for model_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
            for tdir in sorted(p for p in model_dir.iterdir() if p.is_dir()):
                task = tasks.get(tdir.name)
                if not task or not _matches(tdir.name, selector):
                    continue
                old = read_json(tdir / "score.json", {})
                metrics = read_json(tdir / "metrics.json")
                if not metrics:
                    continue
                if old.get("scored_by") == "human":
                    skipped_human.append(f"{model_dir.name}/{tdir.name}")
                    continue
                if task.scoring_type in ("pytest", "webapp", "response"):
                    ws = tdir / "workspace"
                    if not ws.is_dir() or old.get("status") != "scored":
                        continue
                    rec = scoring.run_pytest_checker(task, ws)
                elif task.scoring_type == "answer":
                    text = _final_response(tdir)
                    if text is None:
                        continue
                    rec = scoring.score_answer(task, text)
                else:
                    continue
                rec["summary"] += " (rescored)"
                write_json(tdir / "score.json", rec)
                mark = "" if old.get("score") == rec["score"] else "  <-- changed"
                progress(f"{run_dir.name} {model_dir.name} {tdir.name}: "
                         f"{old.get('score')} -> {rec['score']}{mark}")
                n += 1
    report.generate_all()
    if skipped_human:
        progress(f"{len(skipped_human)} human-graded result(s) LEFT ALONE: "
                 + ", ".join(skipped_human))
    progress(f"{n} result(s) rescored; reports regenerated")
    return n
