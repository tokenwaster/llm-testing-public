#!/usr/bin/env python3
"""Print line and word statistics for a text file."""

import re
import sys
from collections import Counter
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} <path-to-text-file>", file=sys.stderr)
        raise SystemExit(2)

    text = Path(sys.argv[1]).read_text(encoding="utf-8")

    line_count = text.count("\n")
    if text and not text.endswith("\n"):
        line_count += 1

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
