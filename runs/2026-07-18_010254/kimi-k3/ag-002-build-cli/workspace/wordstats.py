#!/usr/bin/env python3
"""wordstats.py — print line count, word count, and the most frequent word.

Usage: python wordstats.py <path-to-text-file>

A *word* is a maximal run of ASCII letters (a-z) after lowercasing the
whole text. Digits, punctuation and underscores separate words.
"""

import re
import sys
from collections import Counter


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as exc:
        print(f"wordstats: cannot read {path!r}: {exc}", file=sys.stderr)
        return 1

    # Lines: split on '\n'; a trailing final newline does not add a line.
    # An empty file has 0 lines.
    if text == "":
        lines = 0
    else:
        lines = len(text.split("\n"))
        if text.endswith("\n"):
            lines -= 1

    # Words: maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", text.lower())
    total_words = len(words)

    if words:
        counts = Counter(words)
        # Most frequent; ties broken alphabetically (earliest wins).
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        top_line = f"top: {top_word} {top_count}"
    else:
        top_line = "top: - 0"

    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(top_line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
