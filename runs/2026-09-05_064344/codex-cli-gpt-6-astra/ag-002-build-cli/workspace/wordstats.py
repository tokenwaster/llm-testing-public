"""Print line, word, and most frequent word counts for a text file."""

import argparse
from collections import Counter
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    text = args.path.read_text(encoding="utf-8")
    lines = text.count("\n") + int(bool(text) and not text.endswith("\n"))
    counts = Counter(re.findall(r"[a-z]+", text.lower()))
    top = min(counts, key=lambda word: (-counts[word], word)) if counts else "-"
    print(f"lines: {lines}")
    print(f"words: {sum(counts.values())}")
    print(f"top: {top} {counts[top] if counts else 0}")


if __name__ == "__main__":
    main()
