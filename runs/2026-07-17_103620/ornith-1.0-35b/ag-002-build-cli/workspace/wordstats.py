#!/usr/bin/env python3
"""Command-line tool to compute word statistics from a text file."""

import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Count lines: split by newline, strip trailing empty element from final \n
    if content == "":
        line_count = 0
    else:
        parts = content.split("\n")
        if parts and parts[-1] == "":
            parts = parts[:-1]
        line_count = len(parts)

    # Words: lowercase, then find maximal runs of ASCII letters
    words = re.findall(r"[a-z]+", content.lower())
    word_count = len(words)

    # Top word
    if word_count == 0:
        top_line = "top: - 0"
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        # Among ties, pick alphabetically first (smallest string)
        candidates = [w for w, c in counter.items() if c == max_count]
        top_word = min(candidates)
        top_line = f"top: {top_word} {max_count}"

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(top_line)


if __name__ == "__main__":
    main()
