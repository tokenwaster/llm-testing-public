#!/usr/bin/env python3
"""Command-line tool to compute word statistics from a text file."""

import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Count lines: trailing final newline does not add an extra line.
    stripped = content.rstrip("\n")
    if stripped == "":
        num_lines = 0 if content == "" else 1
    else:
        num_lines = len(stripped.split("\n"))

    # Extract words: maximal runs of ASCII letters after lowercasing.
    text_lower = content.lower()
    words = re.findall(r"[a-z]+", text_lower)
    total_words = len(words)

    # Find top word (most frequent; ties broken alphabetically).
    if not words:
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print("top: - 0")
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        top_word = sorted(w for w, c in counter.items() if c == max_count)[0]
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print(f"top: {top_word} {max_count}")


if __name__ == "__main__":
    main()
