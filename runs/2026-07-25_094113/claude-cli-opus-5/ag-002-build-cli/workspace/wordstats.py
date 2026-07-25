#!/usr/bin/env python3
"""Print line count, word count and the most frequent word of a text file."""

import re
import sys
from collections import Counter

WORD_RE = re.compile(r"[a-z]+")


def main(argv):
    if len(argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2

    try:
        with open(argv[1], "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if text == "":
        lines = 0
    else:
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)

    words = WORD_RE.findall(text.lower())
    counts = Counter(words)
    # min() over (-count, word) gives highest count, alphabetically first on ties
    top_word, top_count = min(
        ((w, c) for w, c in counts.items()), key=lambda wc: (-wc[1], wc[0])
    ) if counts else ("-", 0)

    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
