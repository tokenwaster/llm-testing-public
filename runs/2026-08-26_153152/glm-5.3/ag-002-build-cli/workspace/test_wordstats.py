#!/usr/bin/env python3
"""Tests for wordstats.py."""

import os
import subprocess
import sys
import tempfile

TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wordstats.py")
PY = sys.executable


def run_tool(path):
    proc = subprocess.run(
        [PY, TOOL, path], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout, proc.stderr


def check(name, content, expected_lines, expected_words, expected_top,
           expected_count, binary=False):
    mode = "wb" if binary else "w"
    with tempfile.NamedTemporaryFile(mode, suffix=".txt", delete=False) as fh:
        fh.write(content)
        path = fh.name
    try:
        code, out, err = run_tool(path)
        expected = (
            "lines: {}\nwords: {}\ntop: {} {}\n".format(
                expected_lines, expected_words, expected_top, expected_count
            )
        )
        ok = (code == 0 and out == expected)
        status = "PASS" if ok else "FAIL"
        print("[{}] {}".format(status, name))
        if not ok:
            print("   exit code : {!r}".format(code))
            print("   stdout    : {!r}".format(out))
            print("   expected  : {!r}".format(expected))
            print("   stderr    : {!r}".format(err))
        return ok
    finally:
        os.unlink(path)


def main():
    results = []

    # --- basic sample -------------------------------------------------
    # line1: the quick brown fox jumps over the lazy dog   -> 9 words, the x2
    # line2: the dog barks the fox runs                     -> 6 words, the x2
    # line3: numbers like and separate words                -> 5 words
    # line4: mixedcase and under scores and hyphen ated ... -> 8 words
    sample = (
        "The quick brown fox jumps over the lazy dog.\n"
        "The dog barks; the fox runs!\n"
        "Numbers like 42 and 3_14 separate words.\n"
        "MixedCase and UNDER_scores and hyphen-ated words.\n"
    )
    results.append(check("basic sample", sample, 4, 28, "the", 4))

    # --- empty file ---------------------------------------------------
    results.append(check("empty file", "", 0, 0, "-", 0))

    # --- only a newline ------------------------------------------------
    results.append(check("single newline", "\n", 1, 0, "-", 0))

    # --- no trailing newline -------------------------------------------
    results.append(check("no trailing newline", "one two three", 1, 3, "one", 1))

    # --- blank lines in the middle -------------------------------------
    results.append(check("blank lines", "a\n\nb\n", 3, 2, "a", 1))

    # --- digits/underscore split words ---------------------------------
    results.append(check("digit separators", "abc123def_ghi", 1, 3, "abc", 1))

    # --- tie broken alphabetically -------------------------------------
    results.append(check("alphabetical tie", "banana apple cherry apple banana",
                         1, 5, "apple", 2))

    # --- tie with counts of 1 ------------------------------------------
    results.append(check("all singletons", "zebra yak xray", 1, 3, "xray", 1))

    # --- case insensitivity --------------------------------------------
    results.append(check("case folding", "Apple APPLE apple aPpLe", 1, 4,
                         "apple", 4))

    # --- CRLF line endings ---------------------------------------------
    results.append(check("crlf endings", "alpha beta\r\ngamma alpha\r\n", 2, 4,
                         "alpha", 2))

    # --- non-ASCII letters are separators ------------------------------
    # "café résumé naïve" -> caf r sum na ve
    results.append(check("non-ascii separators", "caf\u00e9 r\u00e9sum\u00e9 na\u00efve",
                         1, 5, "caf", 1))

    # --- apostrophes split words ---------------------------------------
    # "don't stop it's don't" -> don t stop it s don t
    results.append(check("apostrophes", "don't stop it's don't", 1, 7,
                         "don", 2))

    # --- binary-ish / latin-1 fallback ---------------------------------
    # "olé olé olé" -> ol ol ol
    results.append(check("latin-1 bytes", b"ol\xe9 ol\xe9 ol\xe9\n", 1, 3,
                         "ol", 3, binary=True))

    # --- long-ish generated file ---------------------------------------
    # per line: line has some words words words in it -> 8 words, words x3
    body = "\n".join(
        "line {} has some Words words WORDS in it".format(i) for i in range(50)
    ) + "\n"
    results.append(check("generated 50 lines", body, 50, 400, "words", 150))

    # --- usage error (no args) -----------------------------------------
    proc = subprocess.run([PY, TOOL], capture_output=True, text=True)
    ok = proc.returncode != 0 and proc.stdout == ""
    print("[{}] usage error exits nonzero, no stdout".format(
        "PASS" if ok else "FAIL"))
    results.append(ok)

    # --- missing file ---------------------------------------------------
    proc = subprocess.run([PY, TOOL, os.path.join(tempfile.gettempdir(),
                                                  "definitely_missing_zz.txt")],
                          capture_output=True, text=True)
    ok = proc.returncode != 0 and proc.stdout == ""
    print("[{}] missing file exits nonzero, no stdout".format(
        "PASS" if ok else "FAIL"))
    results.append(ok)

    print()
    print("{}/{} tests passed".format(sum(results), len(results)))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
