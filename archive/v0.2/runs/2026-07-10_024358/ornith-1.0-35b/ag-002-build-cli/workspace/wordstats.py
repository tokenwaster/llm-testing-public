#!/usr/bin/env python3
"""Command-line tool to compute word statistics for a text file."""

import re
import sys
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Count lines: split by newline; trailing final newline does not add extra line.
    if text == "":
        num_lines = 0
    else:
        num_lines = len(text.splitlines())

    # Words: maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", text.lower())
    total_words = len(words)

    if total_words == 0:
        top_line = "top: - 0"
    else:
        counter = Counter(words)
        # Find max count, then among ties pick alphabetically first word.
        max_count = max(counter.values())
        candidates = sorted(w for w, c in counter.items() if c == max_count)
        top_line = f"top: {candidates[0]} {max_count}"

    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(top_line)


if __name__ == "__main__":
    main()
