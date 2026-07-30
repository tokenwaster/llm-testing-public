import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from harness import scoring

HERE = Path(__file__).resolve().parent
TASK = ROOT / "tasks" / "one-shot-apps" / "web-012-coin"

EXPECT = [
    (HERE / "app.html", "reference", 0.8),
    (HERE / "traps" / "app_empty.html", "trap: empty", 0.0),
    (HERE / "traps" / "app_flat.html", "trap: flat disc", (1 / 13) * 0.8),
    (HERE / "traps" / "app_sameface.html", "control: same face", 0.8),
]


def _meta():
    import yaml
    return yaml.safe_load((TASK / "meta.yaml").read_text(encoding="utf-8"))


class _T:
    id = "web-012-coin"
    category = "one-shot-apps"
    checker = TASK / "checker.py"
    checker_timeout_s = 600
    scoring = _meta()["scoring"]


def _out(s):
    sys.stdout.buffer.write((s + "\n").encode("utf-8", "replace"))


def score(app: Path):
    with tempfile.TemporaryDirectory() as d:
        ws = Path(d)
        shutil.copyfile(app, ws / "app.html")
        return scoring.run_pytest_checker(_T(), ws).get("score")


def main() -> int:
    bad = 0
    for app, label, want in EXPECT:
        got = score(app)
        ok = got is not None and abs(got - want) < 5e-3
        bad += 0 if ok else 1
        shown = "None" if got is None else format(got, ".3f")
        _out(f"{'OK  ' if ok else 'FAIL'} {label:20} want {want:.3f}  got {shown}")
    _out("\nweb-012-coin reference-verified" if not bad
         else f"\n{bad} expectation(s) missed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
