"""Reference-verify response-lane tasks: the known-good reply must score 1.0 and
an empty reply must score 0.0 (rule #5). Also reports the trap (bad.txt) score —
a plausible-but-wrong reply — as a discrimination sanity check; it is not gated,
since a partly-right answer legitimately earns partial credit.

Usage:  python tasks-refs/_verify_response.py [task-id ...]
        (no args = every tasks-refs/<id> that has a good.txt)
"""
import sys
import tempfile
from pathlib import Path

from harness import scoring
from harness.tasks import load_tasks

REF = Path(__file__).parent


def _score(task, resp: str) -> float:
    with tempfile.TemporaryDirectory() as d:
        ws = Path(d)
        (ws / "response.txt").write_text(resp, encoding="utf-8")
        return scoring.run_pytest_checker(task, ws)["score"]


def verify(tid: str, tasks: dict) -> bool:
    task = tasks.get(tid)
    if task is None:
        print(f"{tid:28s} FAIL — not a loaded task")
        return False
    good = (REF / tid / "good.txt").read_text(encoding="utf-8")
    bad = (REF / tid / "bad.txt").read_text(encoding="utf-8")
    g, e, b = _score(task, good), _score(task, ""), _score(task, bad)
    ok = abs(g - 1.0) < 1e-9 and e == 0.0
    print(f"{tid:28s} good={g:.3f} empty={e:.3f} trap={b:.3f}  "
          f"{'ok' if ok else 'FAIL (good must be 1.0, empty must be 0.0)'}")
    return ok


if __name__ == "__main__":
    tasks = {t.id: t for t in load_tasks()}
    ids = sys.argv[1:] or sorted(
        d.name for d in REF.iterdir() if (d / "good.txt").is_file())
    allok = all(verify(t, tasks) for t in ids)
    print("\n" + ("ALL VERIFIED" if allok else "*** VERIFICATION FAILED ***"))
    sys.exit(0 if allok else 1)
