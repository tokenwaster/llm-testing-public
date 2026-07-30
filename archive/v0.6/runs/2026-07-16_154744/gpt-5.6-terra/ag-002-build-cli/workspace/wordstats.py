#!/usr/bin/env python3
"""Print line, word, and most-frequent-word statistics for a text file."""

import re
import sys
from collections import Counter


def line_count(text: str) -> int:
    """Count lines separated by LF, without counting a final empty segment."""
    if not text:
        return 0
    return len(text.split("\n")) - (1 if text.endswith("\n") else 0)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        raise SystemExit(2)

    with open(sys.argv[1], "r", encoding="utf-8") as text_file:
        text = text_file.read()

    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)

    if counts:
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count(text)}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
