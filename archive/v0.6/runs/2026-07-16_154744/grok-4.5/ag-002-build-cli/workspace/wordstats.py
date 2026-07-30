#!/usr/bin/env python3
"""Count lines, words, and the most frequent word in a text file."""

import re
import sys
from collections import Counter


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Lines: split by newline; trailing final newline does not add an extra line
    if text == "":
        lines = 0
    else:
        lines = len(text.splitlines())

    # Words: maximal runs of ASCII letters after lowercasing
    words = re.findall(r"[a-z]+", text.lower())
    total_words = len(words)

    if total_words == 0:
        top_word, top_count = "-", 0
    else:
        counts = Counter(words)
        top_word, top_count = min(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        )

    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
