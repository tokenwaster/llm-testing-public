#!/usr/bin/env python3
"""Print line, word, and most-frequent-word statistics for a text file."""

import re
import sys
from collections import Counter


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} <path-to-text-file>")

    with open(sys.argv[1], "r", encoding="utf-8") as file:
        text = file.read()

    # splitlines() does not count the empty portion after a trailing newline.
    line_count = len(text.splitlines())
    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)
    if counts:
        word, count = min(counts.items(), key=lambda item: (-item[1], item[0]))
    else:
        word, count = "-", 0

    print(f"lines: {line_count}")
    print(f"words: {len(words)}")
    print(f"top: {word} {count}")


if __name__ == "__main__":
    main()
