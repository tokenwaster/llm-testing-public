#!/usr/bin/env python3
"""Print line count, word count, and the most frequent word of a text file.

Usage: python wordstats.py <path-to-text-file>
"""
import re
import sys
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    # Line count: newline-split, trailing final newline does not add a line.
    if text == "":
        lines = 0
    else:
        lines = text.count("\n")
        if not text.endswith("\n"):
            lines += 1

    words = re.findall(r"[a-z]+", text.lower())
    print(f"lines: {lines}")
    print(f"words: {len(words)}")

    if not words:
        print("top: - 0")
    else:
        counts = Counter(words)
        # Ties broken alphabetically: max count, then earliest word.
        top_word = min(counts, key=lambda w: (-counts[w], w))
        print(f"top: {top_word} {counts[top_word]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
