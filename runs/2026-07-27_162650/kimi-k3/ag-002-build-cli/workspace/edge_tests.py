import os
import subprocess
import sys

CASES = []

# 1. Empty file
CASES.append(("", ["lines: 0", "words: 0", "top: - 0"]))

# 2. No trailing newline, tie broken alphabetically (beta 2, alpha 2 -> alpha)
CASES.append(("beta beta\nalpha alpha", ["lines: 2", "words: 4", "top: alpha 2"]))

# 3. Trailing newline adds no extra line
CASES.append(("one\n", ["lines: 1", "words: 1", "top: one 1"]))

# 4. Digits/punctuation/underscores split words: foo, bar, baz, qux
CASES.append(("foo_bar2baz!qux", ["lines: 1", "words: 4", "top: bar 1"]))

# 5. No words; "x\n\n" is 2 lines
CASES.append(("123 !! _ _\n\n", ["lines: 2", "words: 0", "top: - 0"]))

# 6. CRLF: \r is not a letter, words unaffected
CASES.append(("ab ab\r\ncd", ["lines: 2", "words: 3", "top: ab 2"]))

# 7. Blank line in the middle counts
CASES.append(("a\n\nb", ["lines: 3", "words: 2", "top: a 1"]))

ok = True
for i, (text, expected) in enumerate(CASES, 1):
    fname = f"_edge_{i}.txt"
    with open(fname, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    proc = subprocess.run(
        [sys.executable, "wordstats.py", fname], capture_output=True, text=True
    )
    got = proc.stdout.splitlines()
    if got == expected and proc.returncode == 0:
        print(f"case {i}: PASS")
    else:
        ok = False
        print(f"case {i}: FAIL\n  expected {expected}\n  got      {got}")
    os.remove(fname)

sys.exit(0 if ok else 1)
