#!/usr/bin/env python3
"""wordstats.py - simple word statistics tool.

Usage: python wordstats.py <path-to-text-file>

Prints:
    lines: <number of lines>
    words: <total word count>
    top:   <most frequent word> <count>
"""
import re
import sys
from collections import Counter


def main(argv):
    if len(argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 1

    path = argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Number of lines: splitlines() treats a trailing newline correctly and
    # gives zero lines for an empty file.
    num_lines = len(text.splitlines())

    # Words: maximal runs of ASCII letters (a-z) after lowercasing.
    lower = text.lower()
    words = re.findall(r"[a-z]+", lower)
    num_words = len(words)

    if num_words == 0:
        top_word, top_count = "-", 0
    else:
        counts = Counter(words)
        # Ties broken alphabetically (earliest wins), then by highest count.
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    print(f"lines: {num_lines}")
    print(f"words: {num_words}")
    print(f"top: {top_word} {top_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
