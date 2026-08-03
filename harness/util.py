
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def terminate_tree(proc) -> None:
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

    def __init__(self, returncode, stdout, stderr, timed_out):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.timed_out = timed_out


SECRET_SUFFIXES = ("_API_KEY", "_TOKEN", "_SECRET", "_PASSWORD")
SECRET_PREFIXES = ("ANTHROPIC_", "OPENAI_", "CLAUDE_CODE_", "AWS_", "AZURE_",
                   "GOOGLE_", "HF_", "HUGGINGFACE_")
SECRET_EXACT = ("MOONSHOT_API_KEY", "OPENROUTER_API_KEY", "LMSTUDIO_API_KEY")


def is_secret_var(name: str) -> bool:
    up = (name or "").upper()
    return (up in SECRET_EXACT
            or up.endswith(SECRET_SUFFIXES)
            or up.startswith(SECRET_PREFIXES))


def child_env(extra: dict | None = None, keep: tuple = ()) -> dict:
    import os
    keep_up = {k.upper() for k in keep}
    env = {k: v for k, v in os.environ.items()
           if k.upper() in keep_up or not is_secret_var(k)}
    if extra:
        env.update(extra)
    return env


def run_capped(cmd, timeout: float, **kwargs) -> CappedResult:
    kwargs.setdefault("stdout", subprocess.PIPE)
    kwargs.setdefault("stderr", subprocess.PIPE)
    kwargs.setdefault("text", True)
    kwargs.setdefault("env", child_env())
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
