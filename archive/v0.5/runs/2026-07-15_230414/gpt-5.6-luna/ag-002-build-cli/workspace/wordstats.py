#!/usr/bin/env python3
"""Print basic word statistics for a text file."""

import re
import sys
from collections import Counter


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} <path-to-text-file>")

    with open(sys.argv[1], "r", encoding="utf-8") as file:
        text = file.read()

    # splitlines() counts physical lines without adding a line for a final
    # newline; an empty file has no lines.
    line_count = len(text.splitlines())
    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)

    if counts:
        word, count = min(counts.items(), key=lambda item: (-item[1], item[0]))
        top = f"{word} {count}"
    else:
        top = "- 0"

    print(f"lines: {line_count}")
    print(f"words: {len(words)}")
    print(f"top: {top}")


if __name__ == "__main__":
    main()
