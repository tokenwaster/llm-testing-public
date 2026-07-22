import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def run_tool(content: str, tmp_path: Path) -> list[str]:
    sample = tmp_path / "sample.txt"
    sample.write_text(content, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(HERE / "wordstats.py"), str(sample)],
        capture_output=True, text=True, encoding="utf-8", timeout=30, cwd=str(HERE))
    assert proc.returncode == 0, f"non-zero exit: {proc.stderr}"
    return [l.rstrip() for l in proc.stdout.strip().splitlines()]


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
