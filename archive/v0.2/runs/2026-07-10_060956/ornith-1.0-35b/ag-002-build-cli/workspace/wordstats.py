#!/usr/bin/env python3
"""Command-line tool to compute line/word stats for a text file."""

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

    # Count lines: split by '\n'; trailing final newline does not add an extra line.
    if content == "":
        num_lines = 0
    else:
        parts = content.split("\n")
        if parts[-1] == "":
            parts.pop()
        num_lines = len(parts)

    # Words: maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", content.lower())
    total_words = len(words)

    # Top word (most frequent; ties broken alphabetically).
    if not words:
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print("top: - 0")
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        # Among all words with the max count, pick alphabetically first.
        top_word = min(w for w, c in counter.items() if c == max_count)
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print(f"top: {top_word} {max_count}")


if __name__ == "__main__":
    main()
