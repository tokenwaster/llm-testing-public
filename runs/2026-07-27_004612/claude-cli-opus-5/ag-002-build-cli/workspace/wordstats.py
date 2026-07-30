#!/usr/bin/env python3
"""Print line count, word count and most frequent word of a text file."""

import re
import sys
from collections import Counter

WORD_RE = re.compile(r"[a-z]+")


def main(argv):
    if len(argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2

    with open(argv[1], "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    if text == "":
        lines = 0
    else:
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)

    words = WORD_RE.findall(text.lower())
    counts = Counter(words)

    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    if counts:
        word, count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        print(f"top: {word} {count}")
    else:
        print("top: - 0")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
