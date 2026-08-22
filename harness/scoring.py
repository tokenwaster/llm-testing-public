
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import config
from .tasks import Task
from .util import now_iso, run_capped

CODE_BLOCK_RE = re.compile(r"```(?:python3?|py3?)?[ \t]*\n(.*?)```",
                           re.DOTALL | re.IGNORECASE)
HTML_BLOCK_RE = re.compile(r"```html\s*\n(.*?)```", re.DOTALL)
ANSWER_RE = re.compile(
    r"^\s*[*_`]*\s*ANSWER\s*[*_`]*\s*:\s*[*_`]*\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE)
CONTROL_TOKEN_RE = re.compile(
    r"<\|[^|>]*\|>|</?s>|<\|?endoftext\|?>"
    r"|<(?:end|start)_of_turn>|<eos>|<bos>|<\uff5c[^\uff5c>]*\uff5c>")
PYTEST_PASSED_RE = re.compile(r"(\d+) passed")
PYTEST_FAILED_RE = re.compile(r"(\d+) failed")
PYTEST_ERROR_RE = re.compile(r"(\d+) errors?\b")
PYTEST_SUMMARY_LINE_RE = re.compile(
    r"^=*\s*(?:\d+ (?:passed|failed|errors?|skipped|xfailed|xpassed|warnings?"
    r"|deselected)(?:,\s*)?)+.*\bin \d")
PYTEST_CONFIG_FILES = ("pytest.ini", "pyproject.toml", "tox.ini",
                       "setup.cfg", ".pytest.ini")
HARNESS_INI = "_harness_pytest.ini"
PYTEST_COLLECT_RE = re.compile(r"ERROR collecting|errors? during collection")
SUBMISSION_BROKE_RE = re.compile(
    r"^E\s+((?:Syntax|Indentation|Tab|Import|ModuleNotFound|Name|Attribute|Type|Value)"
    r"Error.*)$", re.M)


def extract_code_block(text: str) -> str | None:
    blocks = CODE_BLOCK_RE.findall(text)
    if not blocks:
        return None
    code = [b for b in blocks if re.search(r"^\s*(def|class|import|from)\s",
                                           b, re.M)]
    return (code or blocks)[-1].strip() + "\n"


def extract_html_block(text: str) -> str | None:
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
    if not matches:
        return None
    return matches[-1].strip().strip("*`_ \t")


def run_pytest_checker(task: Task, workspace: Path) -> dict:
    checker = task.checker
    if checker is None:
        return _record(0.0, "checker", "missing checker.py")
    target = workspace / "test_checker.py"
    shutil.copyfile(checker, target)
    ini = workspace / HARNESS_INI
    ini.write_text("[pytest]\n", encoding="utf-8")
    cmd = [sys.executable, "-I", "-m", "pytest", str(target.name), "-q",
           "--tb=line", "-p", "no:cacheprovider", "--color=no",
           "--noconftest", "-c", HARNESS_INI, "--rootdir", "."]
    timeout = task.checker_timeout_s
    from .util import child_env
    env = child_env()
    env["PYTEST_ADDOPTS"] = ""
    env.pop("PYTEST_PLUGINS", None)
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
    try:
        proc = run_capped(
            cmd, timeout, cwd=str(workspace), text=True,
            encoding="utf-8", errors="replace", env=env,
            stdin=subprocess.DEVNULL)
    finally:
        ini.unlink(missing_ok=True)
    if proc.timed_out:
        return _record(0.0, "checker", f"checker timed out after {timeout}s")
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    passed, failed = _tally(out)
    total = passed + failed
    if passed == 0 and PYTEST_COLLECT_RE.search(out):
        why = SUBMISSION_BROKE_RE.search(out)
        reason = why.group(1).strip() if why else "the test module could not be imported"
        return _record(0.0, "checker",
                       f"submission does not import — no test ran ({reason})",
                       detail=_tail(out))
    if total == 0:
        return _record(0.0, "checker", f"no tests ran (exit {proc.returncode})",
                       detail=_tail(out))
    cap = float(task.scoring.get("automated_max", 1.0))
    frac = passed / total
    score = frac * cap
    note = (f" (machine max {cap:g}; craft is graded on /review)"
            if cap < 1.0 else "")
    gate = task.scoring.get("gate") or {}
    sub = gate.get("when_failed", "")
    if sub and re.search(rf"(?im)^FAILED[^\n]*{re.escape(sub)}", out):
        gcap = float(gate.get("cap", 0.5))
        if score > gcap:
            score = gcap
            note += f" · GATE FAILED ({sub}): capped at {gcap:g}"
    return _record(score, "checker",
                   f"{passed}/{total} tests passed" + note, detail=_tail(out))


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


def _tally(out: str) -> tuple[int, int]:
    """Counts from pytest's FINAL summary line only. Short-summary lines
    ("FAILED t - AssertionError: 100 passed") and warnings print before it and
    carry model-controlled text, so the first match in the output is not the
    tally."""
    for line in reversed(out.splitlines()):
        if PYTEST_SUMMARY_LINE_RE.match(line.strip()):
            return (_first_int(PYTEST_PASSED_RE, line),
                    _first_int(PYTEST_FAILED_RE, line)
                    + _first_int(PYTEST_ERROR_RE, line))
    return 0, 0


def _tail(text: str, lines: int = 30) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])
