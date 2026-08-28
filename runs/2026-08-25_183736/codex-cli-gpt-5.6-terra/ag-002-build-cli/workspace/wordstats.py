"""Print line, word, and most-common-word statistics for a text file."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


def line_count(text: str) -> int:
    """Count lines split by newlines, excluding a trailing empty split."""
    if not text:
        return 0
    return len(text.splitlines())


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python wordstats.py <path-to-text-file>")

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
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
