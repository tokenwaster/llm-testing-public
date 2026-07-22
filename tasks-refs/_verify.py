"""Reference-verify staged ANSWER tasks: correct answer must score 1.0, and
empty / wrong / no-ANSWER-line must score 0.0. Usage:

    python tasks-refs/_verify.py <staged-task-dir> [<staged-task-dir> ...]
"""
import sys
from pathlib import Path

import yaml

from harness import scoring


class _T:
    def __init__(self, m):
        self.id = m["id"]
        self.category = m["category"]
        self.scoring = m["scoring"]


def verify(task_dir: Path) -> bool:
    meta = yaml.safe_load((task_dir / "meta.yaml").read_text(encoding="utf-8"))
    t = _T(meta)
    ans = str(meta["scoring"]["answer"])
    mt = meta["scoring"].get("match", "exact")
    wrong = "0" if mt == "numeric" else "DEFINITELY-WRONG-XYZ"
    cases = {
        "correct": (f"Working it out...\nANSWER: {ans}", 1.0),
        "empty": ("", 0.0),
        "wrong": (f"ANSWER: {wrong}", 0.0),
        "no-line": (f"the answer is probably {ans} i think", 0.0),
    }
    ok = True
    print(f"\n{task_dir.name}  (answer={ans!r}, match={mt})")
    for name, (resp, want) in cases.items():
        got = scoring.score_answer(t, resp)["score"]
        good = got == want
        ok &= good
        print(f"  {'ok ' if good else 'FAIL'} {name:8s} score={got} (want {want})")
    return ok


if __name__ == "__main__":
    dirs = [Path(a) for a in sys.argv[1:]]
    allok = all(verify(d) for d in dirs)
    print("\n" + ("ALL VERIFIED" if allok else "*** VERIFICATION FAILED ***"))
    sys.exit(0 if allok else 1)
