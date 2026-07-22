#!/usr/bin/env python3
"""Command-line tool to compute word statistics from a text file."""

import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Count lines: split by newline; trailing final newline does not add an extra line.
    if content == "":
        num_lines = 0
    else:
        parts = content.split("\n")
        if parts and parts[-1] == "":
            parts = parts[:-1]
        num_lines = len(parts)

    # Words: maximal runs of ASCII letters (a-z) after lowercasing.
    words = re.findall(r"[a-z]+", content.lower())
    total_words = len(words)

    # Top word by frequency, ties broken alphabetically (earliest wins).
    if not words:
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print("top: - 0")
    else:
        counter = Counter(words)
        # Sort by (-count, word) to get highest count first, then alphabetically.
        top_word, top_count = sorted(counter.items(), key=lambda x: (-x[1], x[0]))[0]
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
