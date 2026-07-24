"""Reference-verify web-013-billiards through the real scoring lane. Run:

    python tasks-refs/web-013-billiards/verify.py

Expects:
    app.html               -> 0.800  playable + all physics; machine max is 0.8,
                                      the last 0.2 is fit-and-finish on /review
    traps/app_empty        -> 0.000  no window.sim: fails everything
    traps/app_static       -> low    API present, no physics, unplayable
    traps/app_physics_only -> 0.500  perfect physics but NOT playable (no shot,
                                      no reset, no instructions): the gate caps it
"""
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from harness import scoring

HERE = Path(__file__).resolve().parent
TASK = ROOT / "tasks" / "one-shot-apps" / "web-013-billiards"


def _meta():
    import yaml
    return yaml.safe_load((TASK / "meta.yaml").read_text(encoding="utf-8"))


class _T:
    id = "web-013-billiards"
    category = "one-shot-apps"
    checker = TASK / "checker.py"
    checker_timeout_s = 300
    scoring = _meta()["scoring"]


def score(app: Path):
    with tempfile.TemporaryDirectory() as d:
        ws = Path(d)
        shutil.copyfile(app, ws / "app.html")
        return scoring.run_pytest_checker(_T(), ws).get("score")


def main() -> int:
    ref = score(HERE / "app.html")
    empty = score(HERE / "traps" / "app_empty.html")
    static = score(HERE / "traps" / "app_static.html")
    physics = score(HERE / "traps" / "app_physics_only.html")
    print(f"reference     : {ref}   (want 0.800: playable + physics, machine max)")
    print(f"trap empty    : {empty}   (want 0.000)")
    print(f"trap static   : {static}   (want < 0.25)")
    print(f"trap phys-only: {physics}   (want 0.500: gated — unplayable)")
    ok = (ref is not None and abs(ref - 0.8) < 5e-3
          and empty == 0.0 and (static or 0) < 0.25
          and physics is not None and abs(physics - 0.5) < 5e-3)
    print("\nweb-013-billiards reference-verified" if ok
          else "\n*** VERIFICATION FAILED (ref 0.8, empty 0.0, static <0.25, "
               "phys-only 0.5) ***")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
