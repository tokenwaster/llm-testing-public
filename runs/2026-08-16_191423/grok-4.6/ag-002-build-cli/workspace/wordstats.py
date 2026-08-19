#!/usr/bin/env python3
import sys
import re
from collections import Counter


def count_lines(text: str) -> int:
    return len(text.splitlines())


def extract_words(text: str) -> list[str]:
    return re.findall(r"[a-z]+", text.lower())


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    lines = count_lines(text)
    words = extract_words(text)
    total = len(words)

    if total == 0:
        top_word, top_count = "-", 0
    else:
        counts = Counter(words)
        # Highest count first; ties broken alphabetically (earliest wins).
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))

    print(f"lines: {lines}")
    print(f"words: {total}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
