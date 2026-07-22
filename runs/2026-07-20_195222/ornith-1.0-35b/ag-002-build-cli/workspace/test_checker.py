import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
TOOL_TIMEOUT_S = 30


def run_tool(content: str, tmp_path: Path) -> list[str]:
    """Run the model's CLI; on timeout kill it and anything it spawned.

    The kill must happen while the top process lives: taskkill /T walks the live
    tree, and a venv python.exe is a launcher shim hiding the real interpreter.
    """
    sample = tmp_path / "sample.txt"
    sample.write_text(content, encoding="utf-8")
    kw = {}
    if os.name != "nt":
        kw["start_new_session"] = True
    proc = subprocess.Popen(
        [sys.executable, str(HERE / "wordstats.py"), str(sample)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", cwd=str(HERE), **kw)
    try:
        out, err = proc.communicate(timeout=TOOL_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           capture_output=True)
        else:
            import signal
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()
        try:
            proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        raise AssertionError(
            f"the tool did not finish within {TOOL_TIMEOUT_S}s (killed)")
    assert proc.returncode == 0, f"non-zero exit: {err}"
    return [l.rstrip() for l in out.strip().splitlines()]


def test_basic(tmp_path):
    out = run_tool("The cat sat.\nThe dog sat!\n", tmp_path)
    assert out[0] == "lines: 2"
    assert out[1] == "words: 6"
    # 'sat' and 'the' both appear twice; alphabetical tie-break -> sat
    assert out[2] == "top: sat 2"


def test_case_folding(tmp_path):
    out = run_tool("Hello hello HELLO world", tmp_path)
    assert out[0] == "lines: 1"
    assert out[1] == "words: 4"
    assert out[2] == "top: hello 3"


def test_punctuation_and_digits_split(tmp_path):
    out = run_tool("a1a b_b c-c\n", tmp_path)
    # tokens: a, a, b, b, c, c -> 6 words, tie -> 'a'
    assert out[1] == "words: 6"
    assert out[2] == "top: a 2"


def test_no_words(tmp_path):
    out = run_tool("123 456\n789\n", tmp_path)
    assert out[0] == "lines: 2"
    assert out[1] == "words: 0"
    assert out[2] == "top: - 0"
