"""Small shared helpers: time, hashing, safe JSON file IO, killable subprocesses."""

import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def terminate_tree(proc) -> None:
    """Kill `proc` and every descendant it spawned.

    Must be called while `proc` is still alive: taskkill /T walks the live
    parent->child snapshot, and orphans keep a stale PPID once the top exits.
    POSIX kills the process group, so callers pass start_new_session=True.
    """
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True)
    else:
        import signal
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except OSError:
            try:
                proc.kill()
            except OSError:
                pass


class CappedResult:
    """returncode is None when the process was killed; `timed_out` tells that
    apart from a plain non-zero exit."""

    def __init__(self, returncode, stdout, stderr, timed_out):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.timed_out = timed_out


def run_capped(cmd, timeout: float, **kwargs) -> CappedResult:
    """subprocess.run(timeout=), except the timeout reaps the whole tree.

    Use anywhere a deadline can fire on a process that spawns others:
    run(timeout=) kills only the direct child, and a venv python.exe is itself a
    launcher shim, so the real interpreter survives.
    """
    kwargs.setdefault("stdout", subprocess.PIPE)
    kwargs.setdefault("stderr", subprocess.PIPE)
    kwargs.setdefault("text", True)
    if os.name != "nt":
        kwargs.setdefault("start_new_session", True)
    proc = subprocess.Popen(cmd, **kwargs)
    try:
        out, err = proc.communicate(timeout=timeout)
        return CappedResult(proc.returncode, out, err, False)
    except subprocess.TimeoutExpired:
        terminate_tree(proc)
        try:
            out, err = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            out, err = "", ""
        return CappedResult(None, out or "", err or "", True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def now_ms() -> float:
    return time.perf_counter() * 1000.0


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


_HASH_SKIP_DIRS = {"__pycache__", ".pytest_cache"}


def hash_dir(path: Path, patterns: tuple[str, ...] = ("*",)) -> str:
    """Stable content hash of every file under `path` (sorted, recursive).

    Bytecode is NOT content. rglob("*") happily swept __pycache__ in, so simply
    RUNNING a task's checker (python compiles it) changed the task's identity:
    33 of v0.5's 39 tasks recorded two or three different hashes for content
    that never moved, which makes "every result records a hash of the task"
    worthless for spotting real drift. Skip caches so the hash means what it
    claims.
    """
    h = hashlib.sha256()
    files = sorted(p for pat in patterns for p in path.rglob(pat)
                   if p.is_file() and not _HASH_SKIP_DIRS & set(p.parts)
                   and p.suffix not in (".pyc", ".pyo"))
    for f in files:
        h.update(str(f.relative_to(path)).replace("\\", "/").encode("utf-8"))
        h.update(b"\x00")
        h.update(f.read_bytes())
        h.update(b"\x00")
    return h.hexdigest()


def robust_rmtree(path, tries: int = 5, delay: float = 0.3) -> bool:
    """rmtree tolerating Windows file locks and read-only files. A dir can't be
    removed while any process holds a handle (WinError 32 — a just-exited child,
    antivirus, an open editor); read-only files raise WinError 5. Clears the
    read-only bit inline and retries with backoff. True on success, False if
    still stuck — callers should surface that, not crash the request thread."""
    import os
    import shutil
    import stat

    path = Path(path)
    if not path.exists():
        return True

    def _onexc(func, p, exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)

    for i in range(tries):
        try:
            shutil.rmtree(path, onexc=_onexc)
            return True
        except OSError:
            if i == tries - 1:
                return not path.exists()
            time.sleep(delay * (i + 1))
    return not path.exists()


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, data) -> None:
    """Atomic write: readers see either the old file or the new one, never a
    torn half-write — required now that report regeneration can run while a
    benchmark is writing results."""
    import os
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


import threading as _threading
from contextlib import contextmanager

_awake = _threading.local()


@contextmanager
def keep_awake():
    """Block SYSTEM sleep for the wrapped work (Windows); no-op elsewhere.
    Released on exit, or by the OS if the process dies.

    REENTRANT per thread — only the outermost exit releases. Windows' idle
    timer counts from the last user INPUT, so even a millisecond release
    between trials means instant sleep on an idle box: the outermost scope
    must cover the ENTIRE job. State is per-thread — call INSIDE the worker
    thread."""
    import ctypes
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    depth = getattr(_awake, "depth", 0)
    set_state = None
    if depth == 0:
        try:
            set_state = ctypes.windll.kernel32.SetThreadExecutionState
            set_state(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        except (AttributeError, OSError):
            set_state = None
    _awake.depth = depth + 1
    _awake.set_state = set_state if depth == 0 else getattr(
        _awake, "set_state", None)
    try:
        yield
    finally:
        _awake.depth -= 1
        if _awake.depth == 0 and getattr(_awake, "set_state", None):
            try:
                _awake.set_state(ES_CONTINUOUS)
            except OSError:
                pass
            _awake.set_state = None


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[truncated {len(text) - limit} chars]"


import re as _re

_C_BLOCK = _re.compile(r"/\*.*?\*/", _re.S)
_C_WHOLE = _re.compile(r"(?m)^[ \t]*//[^\n]*\n")
_C_INLINE = _re.compile(r"(?<=\S)[ \t]+//[^\n]*")
_C_BLANK = _re.compile(r"\n{3,}")
_PRE = _re.compile(r"<pre\b[^>]*>.*?</pre>", _re.S | _re.I)


def strip_output_comments(s: str) -> str:
    """Strip CSS/JS comments from generated HTML before it ships.

    Applies ONLY outside <pre>: those hold verbatim model output, whose own
    `/* */` and `//` are the evidence the page exists to show — stripping them
    silently rewrites what a model produced, and an unbalanced `/*` in one
    model's code swallows every page element up to the next `*/`.

    Leaves HTML <!-- --> comments alone (ours are the functional navlink/NAV
    markers), and only treats // as a comment when whitespace precedes it, so
    URLs (`https://`, `href="//..."`) survive.
    """
    out, last = [], 0
    for m in _PRE.finditer(s):
        out.append(_strip_css_js(s[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_strip_css_js(s[last:]))
    return "".join(out)


def _strip_css_js(s: str) -> str:
    s = _C_BLOCK.sub("", s)
    s = _C_WHOLE.sub("", s)
    s = _C_INLINE.sub("", s)
    return _C_BLANK.sub("\n\n", s)
