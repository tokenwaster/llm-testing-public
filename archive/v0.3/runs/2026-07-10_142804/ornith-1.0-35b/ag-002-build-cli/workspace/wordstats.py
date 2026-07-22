#!/usr/bin/env python3
"""Command-line tool to compute line count, word count, and top word in a text file."""

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

    # Count lines: trailing newline does not add an extra line.
    if not content:
        num_lines = 0
    else:
        num_lines = len(content.split("\n"))
        if content.endswith("\n"):
            num_lines -= 1

    # Words are maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", content.lower())
    total_words = len(words)

    # Top word: most frequent, ties broken alphabetically (earliest wins).
    if not words:
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print("top: - 0")
    else:
        counter = Counter(words)
        # Sort by (-count, word) so highest count first, then alphabetical.
        top_word, top_count = sorted(counter.items(), key=lambda x: (-x[1], x[0]))[0]
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
