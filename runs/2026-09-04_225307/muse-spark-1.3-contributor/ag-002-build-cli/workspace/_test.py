import subprocess, os, tempfile

def run(content_bytes, suffix=".txt"):
    with tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False) as tf:
        tf.write(content_bytes)
        name = tf.name
    try:
        r = subprocess.run(["python", "wordstats.py", name], capture_output=True, text=True)
        return r.stdout, r.stderr, r.returncode
    finally:
        os.unlink(name)

def check(name, content, expected):
    out, err, code = run(content)
    status = "PASS" if out == expected else "FAIL"
    print(f"--- {name}: {status} ---")
    print(f"content={content!r}")
    print(f"expected={expected!r}")
    print(f"got     ={out!r}")
    if err: print(f"stderr={err!r}")
    print(f"code={code}")

# 1: basic
check("basic", b"Hello world\nHello again\n", "lines: 2\nwords: 4\ntop: hello 2\n")
# 2: no trailing newline
check("no trailing newline", b"Hello world\nHello again", "lines: 2\nwords: 4\ntop: hello 2\n")
# 3: empty file
check("empty", b"", "lines: 0\nwords: 0\ntop: - 0\n")
# 4: only newline?
check("single newline", b"\n", "lines: 1\nwords: 0\ntop: - 0\n")
# 5: tie alphabetical
check("tie", b"b a\n", "lines: 1\nwords: 2\ntop: a 1\n")
# 6: digits punctuation underscores separate
check("separators", b"abc123def_ghi!jkl\n", "lines: 1\nwords: 4\ntop: abc 1\n")
# 7: case insensitivity
check("case", b"Apple APPLE apple banana\n", "lines: 1\nwords: 4\ntop: apple 3\n")
# 8: no words but multiple lines
check("no words", b"123 456\n!!!\n", "lines: 2\nwords: 0\ntop: - 0\n")
# 9: single line no newline
check("single line", b"one two three", "lines: 1\nwords: 3\ntop: one 1\n")
# 10: non-ascii? should be separators
check("unicode", b"Caf\xc3\xa9 caf\xc3\xa9\n", "lines: 1\nwords: 4\ntop: caf 2\n")
