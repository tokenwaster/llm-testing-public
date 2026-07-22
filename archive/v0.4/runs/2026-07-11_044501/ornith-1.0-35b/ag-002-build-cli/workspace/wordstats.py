#!/usr/bin/env python3
"""Command-line tool that reports line count, word count, and top word in a text file."""

import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Count lines: split by newline; trailing final newline does not add an extra line.
    raw_lines = text.split("\n")
    if raw_lines and raw_lines[-1] == "":
        raw_lines.pop()
    num_lines = len(raw_lines)

    # Words: maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", text.lower())
    total_words = len(words)

    # Top word by frequency; ties broken alphabetically (earliest wins).
    if not words:
        top_line = "top: - 0"
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        candidates = sorted(w for w, c in counter.items() if c == max_count)
        top_word = candidates[0]
        top_line = f"top: {top_word} {max_count}"

    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(top_line)


if __name__ == "__main__":
    main()
