#!/usr/bin/env python3
"""wordstats.py - simple word/line statistics for a text file."""

import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    num_lines = len(text.splitlines())

    words = re.findall(r"[a-z]+", text.lower())
    num_words = len(words)

    if num_words == 0:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Tie-break alphabetically (earliest wins): sort by (-count, word)
        top_word, top_count = min(
            counts.items(), key=lambda kv: (-kv[1], kv[0])
        )

    print(f"lines: {num_lines}")
    print(f"words: {num_words}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
