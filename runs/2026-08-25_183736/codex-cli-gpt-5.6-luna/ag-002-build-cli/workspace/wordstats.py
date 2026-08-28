"""Print basic word statistics for a text file."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


def main() -> None:
    text = Path(sys.argv[1]).read_text(encoding="utf-8")

    lines = len(text.splitlines()) if text else 0
    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)

    if counts:
        word, count = min(counts.items(), key=lambda item: (-item[1], item[0]))
    else:
        word, count = "-", 0

    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    print(f"top: {word} {count}")


if __name__ == "__main__":
    main()
