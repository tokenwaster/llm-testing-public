#!/usr/bin/env python3
"""Print line and word statistics for a text file."""

import re
import sys
from collections import Counter


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        raise SystemExit(2)

    with open(sys.argv[1], "r", encoding="utf-8", newline="") as file:
        text = file.read()

    line_count = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)

    if counts:
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
