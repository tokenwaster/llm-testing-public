"""Scoring lanes:

  pytest — copy the task's checker.py into the workspace as test_checker.py,
           run pytest, score = passed / (passed + failed). Syntax/collection
           errors score 0.
  answer — extract the final `ANSWER: ...` line, match against meta
           (exact | numeric | regex).
  response — save the model's RAW reply as response.txt in the workspace, then
           run the task's checker.py against it (same pytest machinery as the
           code lane, but no code workspace and no forced format instruction).
           For constraint/format, structured-extraction, grounded-QA and
           prompt-based tool-call tasks whose whole reply must be inspected.
  manual — mark pending (legacy lane; the review UI was retired).

Every score record carries `scored_by` so methodology stays auditable.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import config
from .tasks import Task
from .util import now_iso, run_capped

CODE_BLOCK_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)
HTML_BLOCK_RE = re.compile(r"```html\s*\n(.*?)```", re.DOTALL)
ANSWER_RE = re.compile(r"^\s*ANSWER:\s*(.+?)\s*$", re.MULTILINE)
CONTROL_TOKEN_RE = re.compile(r"<\|[^|>]*\|>|</?s>|<\|?endoftext\|?>")
PYTEST_PASSED_RE = re.compile(r"(\d+) passed")
PYTEST_FAILED_RE = re.compile(r"(\d+) failed")
PYTEST_ERROR_RE = re.compile(r"(\d+) error")


def extract_code_block(text: str) -> str | None:
    """Last fenced python block wins (models often show sketches first)."""
    blocks = CODE_BLOCK_RE.findall(text)
    return blocks[-1].strip() + "\n" if blocks else None


def extract_html_block(text: str) -> str | None:
    """Last fenced html block wins; falls back to a raw <!doctype/<html document."""
    blocks = HTML_BLOCK_RE.findall(text)
    if blocks:
        return blocks[-1].strip() + "\n"
    stripped = text.strip()
    if stripped.lower().startswith(("<!doctype", "<html")):
        return stripped + "\n"
    return None


def extract_answer(text: str) -> str | None:
    text = CONTROL_TOKEN_RE.sub("", text)
    matches = ANSWER_RE.findall(text)
    return matches[-1].strip() if matches else None


def run_pytest_checker(task: Task, workspace: Path) -> dict:
    """Run the task's checker against the workspace. Returns a score record."""
    checker = task.checker
    if checker is None:
        return _record(0.0, "checker", "missing checker.py")
    target = workspace / "test_checker.py"
    shutil.copyfile(checker, target)
    cmd = [sys.executable, "-m", "pytest", str(target.name), "-q", "--tb=line",
           "-p", "no:cacheprovider", "--color=no"]
    timeout = task.checker_timeout_s
    env = os.environ.copy()
    local_browsers = config.ROOT / ".pw-browsers"
    if local_browsers.is_dir():
        env["PLAYWRIGHT_BROWSERS_PATH"] = str(local_browsers)
    else:
        try:
            home = env.get("USERPROFILE") or env.get("HOME") or str(Path.home())
            env.setdefault("USERPROFILE", home)
            env.setdefault("LOCALAPPDATA", str(Path(home) / "AppData" / "Local"))
            env.setdefault("PLAYWRIGHT_BROWSERS_PATH",
                           str(Path(env["LOCALAPPDATA"]) / "ms-playwright"))
        except (RuntimeError, OSError):
            pass
    proc = run_capped(
        cmd, timeout, cwd=str(workspace), text=True,
        encoding="utf-8", errors="replace", env=env,
        stdin=subprocess.DEVNULL)
    if proc.timed_out:
        return _record(0.0, "checker", f"checker timed out after {timeout}s")
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    passed = _first_int(PYTEST_PASSED_RE, out)
    failed = _first_int(PYTEST_FAILED_RE, out) + _first_int(PYTEST_ERROR_RE, out)
    total = passed + failed
    if total == 0:
        return _record(0.0, "checker", f"no tests ran (exit {proc.returncode})",
                       detail=_tail(out))
    cap = float(task.scoring.get("automated_max", 1.0))
    frac = passed / total
    return _record(frac * cap, "checker",
                   f"{passed}/{total} tests passed"
                   + (f" (machine max {cap:g}; craft is graded on /review)"
                      if cap < 1.0 else ""),
                   detail=_tail(out))


def score_answer(task: Task, response_text: str) -> dict:
    expected = str(task.scoring.get("answer", "")).strip()
    match_type = task.scoring.get("match", "exact")
    got = extract_answer(response_text)
    if got is None:
        return _record(0.0, "checker", "no ANSWER: line found in response")
    if match_type == "exact":
        ok = _norm(got) == _norm(expected)
    elif match_type == "numeric":
        try:
            tol = float(task.scoring.get("tolerance", 1e-6))
            ok = abs(_to_float(got) - float(expected)) <= tol
        except (ValueError, TypeError):
            ok = False
    elif match_type == "regex":
        ok = re.fullmatch(expected, got, re.IGNORECASE) is not None
    else:
        return _record(0.0, "checker", f"unknown match type '{match_type}'")
    summary = f"expected '{expected}', got '{got}' ({match_type})"
    if not ok and _answer_present(expected, match_type, got):
        summary += "  [FORMAT-MISS: expected value inside the ANSWER line]"
    return _record(1.0 if ok else 0.0, "checker", summary)


def _answer_present(expected: str, match_type: str, got: str) -> bool:
    """Expected value present in the ANSWER line despite a failed strict match.
    ANSWER line only — a value merely mentioned in reasoning isn't flagged."""
    clean = _norm(CONTROL_TOKEN_RE.sub("", got))
    if match_type == "numeric":
        try:
            want = float(expected)
        except (ValueError, TypeError):
            return False
        for tok in re.findall(r"-?\d+(?:\.\d+)?(?:/\d+)?", clean):
            try:
                if abs(_to_float(tok) - want) <= 1e-6:
                    return True
            except (ValueError, ZeroDivisionError):
                continue
        return False
    return bool(expected) and _norm(expected) in clean


def pending_manual() -> dict:
    return {"status": "pending", "score": None, "scored_by": None,
            "summary": "awaiting manual review", "timestamp": now_iso()}


def _record(score: float, scored_by: str, summary: str, detail: str = "") -> dict:
    return {"status": "scored", "score": round(score, 4), "scored_by": scored_by,
            "summary": summary, "detail": detail, "timestamp": now_iso()}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().casefold().rstrip(".")


def _to_float(s: str) -> float:
    stripped = re.sub(r"[,$\s]", "", s)
    try:
        if "/" in stripped:
            num, _, den = stripped.partition("/")
            return float(num) / float(den)
        return float(stripped)
    except (ValueError, ZeroDivisionError):
        pass
    m = re.search(r"[-+]?\d*\.?\d+(?:/\d+)?(?=\s|$)", re.sub(r"[,$]", "", s))
    if m is None:
        raise ValueError(f"no numeric value in {s!r}")
    tok = m.group()
    if "/" in tok:
        num, _, den = tok.partition("/")
        return float(num) / float(den)
    return float(tok)


def _first_int(pattern: re.Pattern, text: str) -> int:
    m = pattern.search(text)
    return int(m.group(1)) if m else 0


def _tail(text: str, lines: int = 30) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])
