#!/usr/bin/env python3
"""wordstats.py — print line count, word count, and most frequent word of a text file.

Usage: python wordstats.py <path-to-text-file>
"""

import re
import sys
from collections import Counter


def main(argv):
    if len(argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2

    with open(argv[1], "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Number of lines: split by newline; a trailing final newline does not
    # add an extra line. An empty file has zero lines.
    if text == "":
        lines = 0
    else:
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)

    # Words: maximal runs of ASCII letters a-z after lowercasing the text.
    words = re.findall(r"[a-z]+", text.lower())
    word_count = len(words)

    if words:
        counts = Counter(words)
        # Most frequent word; ties broken alphabetically (earliest wins).
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        top_line = f"top: {top_word} {top_count}"
    else:
        top_line = "top: - 0"

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(top_line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
