#!/usr/bin/env python3
"""Print line, word, and frequency statistics for a text file."""

import re
import sys
from collections import Counter


def main() -> None:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        raise SystemExit(2)

    with open(sys.argv[1], "r", encoding="utf-8") as file:
        text = file.read()

    lines = len(text.splitlines())
    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)

    if counts:
        top_word = min(counts, key=lambda word: (-counts[word], word))
        top_count = counts[top_word]
    else:
        top_word, top_count = "-", 0

    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
