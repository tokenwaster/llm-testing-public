#!/usr/bin/env python3
"""Print line count, word count, and most frequent word for a text file."""

import re
import sys
from collections import Counter


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: python {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        return 2

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    # Line count: split on newline; a trailing newline does not add a line.
    if text == "":
        line_count = 0
    else:
        line_count = text.count("\n") + (0 if text.endswith("\n") else 1)

    # Words: maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)

    if counts:
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
