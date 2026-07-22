#!/usr/bin/env python3
"""Print basic line and word statistics for a text file."""

import re
import sys
from collections import Counter
from pathlib import Path


def line_count(text: str) -> int:
    """Count newline-delimited lines, without an extra trailing empty line."""
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2

    try:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    except OSError as error:
        print(f"wordstats.py: {error}", file=sys.stderr)
        return 1

    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)

    if counts:
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count(text)}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
