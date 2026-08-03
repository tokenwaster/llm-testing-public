import subprocess, sys, textwrap, os

def run(content, suffix=".txt"):
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as f:
        f.write(content)
        name = f.name
    result = subprocess.run(
        [sys.executable, "wordstats.py", name],
        capture_output=True, text=True
    )
    os.unlink(name)
    return result.stdout.strip()

# --- Test 1: basic sample (trailing newline)
out = run("Hello, world! This is a test.\nThe test is simple: count the words.\nWords like hello123world are split by digits.\nhello is the most frequent word here, hello!\n")
assert out == "lines: 4\nwords: 29\ntop: hello 4", f"Test 1 failed:\n{out}"
print("Test 1 passed:", out)

# --- Test 2: no trailing newline
out = run("one two three\nfour five")
assert out == "lines: 2\nwords: 5\ntop: five 1", f"Test 2 failed:\n{out}"
print("Test 2 passed:", out)

# --- Test 3: tie-breaking (alphabetical)
out = run("cat bat cat bat\n")
assert out == "lines: 1\nwords: 4\ntop: bat 2", f"Test 3 failed:\n{out}"
print("Test 3 passed:", out)

# --- Test 4: empty file
out = run("")
assert out == "lines: 0\nwords: 0\ntop: - 0", f"Test 4 failed:\n{out}"
print("Test 4 passed:", out)

# --- Test 5: only digits/punctuation (no words)
out = run("123 456!!! 789\n")
assert out == "lines: 1\nwords: 0\ntop: - 0", f"Test 5 failed:\n{out}"
print("Test 5 passed:", out)

# --- Test 6: digits split words
out = run("hello2world\n")
assert out == "lines: 1\nwords: 2\ntop: hello 1", f"Test 6 failed:\n{out}"
print("Test 6 passed:", out)

# --- Test 7: single line no trailing newline
out = run("the the the")
assert out == "lines: 1\nwords: 3\ntop: the 3", f"Test 7 failed:\n{out}"
print("Test 7 passed:", out)

print("\nAll tests passed!")
