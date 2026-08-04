import subprocess
import sys
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "wordstats.py")


def run(path):
    p = subprocess.run([sys.executable, SCRIPT, path],
                       capture_output=True, text=True)
    assert p.returncode == 0, (p.returncode, p.stderr)
    return p.stdout


def run_text(text):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    try:
        return run(path)
    finally:
        os.remove(path)


cases = [
    # (text, expected stdout)
    ("hello world\nhello there\n", "lines: 2\nwords: 4\ntop: hello 2\n"),
    ("no trailing newline", "lines: 1\nwords: 3\ntop: newline 1\n"),
    ("", "lines: 0\nwords: 0\ntop: - 0\n"),
    ("12345 !!! ___ \n", "lines: 1\nwords: 0\ntop: - 0\n"),
    # tie broken alphabetically: apple and zebra both 2 -> apple
    ("zebra apple zebra apple\n", "lines: 1\nwords: 4\ntop: apple 2\n"),
    # snake_case / digits split words
    ("foo_bar foo2bar\n", "lines: 2\nwords: 4\ntop: bar 2\n".replace("lines: 2", "lines: 1")),
    ("MiXeD case MIXED Case mixed\n", "lines: 1\nwords: 5\ntop: mixed 3\n"),
    ("a\n\nb\n", "lines: 3\nwords: 2\ntop: a 1\n"),
    ("a\n\nb", "lines: 3\nwords: 2\ntop: a 1\n"),
]

for text, expected in cases:
    got = run_text(text)
    assert got == expected, (repr(text), repr(got), repr(expected))
    print("ok:", repr(text[:25]), "->", repr(got))

print("--- sample.txt ---")
print(run(os.path.join(HERE, "sample.txt")), end="")

# usage error
p = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True)
assert p.returncode != 0 and p.stdout == ""
print("ok: usage error handled")
print("ALL TESTS PASSED")
