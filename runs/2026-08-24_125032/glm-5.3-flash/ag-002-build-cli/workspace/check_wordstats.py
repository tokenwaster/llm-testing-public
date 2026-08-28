import re, subprocess, sys

def expected(text):
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    words = re.findall(r"[a-z]+", text.lower())
    if words:
        best = max(sorted(set(words)), key=lambda w: words.count(w))
        # tie-break alphabetically: pick earliest word with max count
        mx = max(words.count(w) for w in set(words))
        best = min(w for w in set(words) if words.count(w) == mx)
        top = f"{best} {mx}"
    else:
        top = "- 0"
    return f"lines: {len(lines)}\nwords: {len(words)}\ntop: {top}"

cases = {
    "sample.txt": open("sample.txt").read(),
    "empty.txt": "",
    "nowords.txt": "123 ___ !!! ... 456\n\t\n--\n",
    "nonewline.txt": "one two two THREE three three",
    "tie.txt": "b b a a c\n",
}

fails = 0
for name, text in cases.items():
    with open(name, "w") as fh:
        fh.write(text)
    got = subprocess.run([sys.executable, "wordstats.py", name],
                         capture_output=True, text=True)
    exp = expected(text)
    ok = got.stdout == exp + "\n"
    print(f"{name}: {'PASS' if ok else 'FAIL'}")
    if not ok:
        fails += 1
        print("  expected:", repr(exp))
        print("  got     :", repr(got.stdout.rstrip("\n")))

# usage / error handling should go to stderr, not stdout
r = subprocess.run([sys.executable, "wordstats.py"], capture_output=True, text=True)
print("no-args stdout empty:", r.stdout == "", "| exit:", r.returncode)
r = subprocess.run([sys.executable, "wordstats.py", "missing_file_xyz.txt"],
                   capture_output=True, text=True)
print("missing-file stdout empty:", r.stdout == "", "| exit:", r.returncode)

print("sample.txt expected vs actual:")
print(expected(cases["sample.txt"]))
r = subprocess.run([sys.executable, "wordstats.py", "sample.txt"],
                   capture_output=True, text=True)
print(r.stdout, end="")

sys.exit(1 if fails else 0)
