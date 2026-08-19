import subprocess
import os
import tempfile

def test(content, expected_output):
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as f:
        f.write(content)
        f_name = f.name
    try:
        res = subprocess.run(['python', 'wordstats.py', f_name], capture_output=True, text=True, check=True)
        assert res.stdout == expected_output, f"Expected {repr(expected_output)}, got {repr(res.stdout)}"
    finally:
        os.remove(f_name)

# Empty file
test("", "lines: 0\nwords: 0\ntop: - 0\n")

# Single newline
test("\n", "lines: 1\nwords: 0\ntop: - 0\n")

# Two newlines
test("\n\n", "lines: 2\nwords: 0\ntop: - 0\n")

# Trailing newline vs no trailing newline
test("abc\ndef", "lines: 2\nwords: 2\ntop: abc 1\n")
test("abc\ndef\n", "lines: 2\nwords: 2\ntop: abc 1\n")

# Tie breaking alphabetically
test("zebra apple", "lines: 1\nwords: 2\ntop: apple 1\n")
test("zebra zebra apple apple", "lines: 1\nwords: 4\ntop: apple 2\n")

# Non-ascii, digits, punctuation, underscores
test("hello_world 123foo456 bar!baz", "lines: 1\nwords: 5\ntop: bar 1\n")

print("All tests passed!")
