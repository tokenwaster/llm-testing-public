#!/usr/bin/env python3
import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r") as f:
        text = f.read()

    # Count lines: split by newline; a trailing empty element from a final newline is not counted.
    raw_lines = text.split("\n")
    if raw_lines and raw_lines[-1] == "":
        line_count = len(raw_lines) - 1
    else:
        line_count = len(raw_lines)

    # Count words: maximal runs of ASCII letters after lowercasing.
    lowered = text.lower()
    words = re.findall(r"[a-z]+", lowered)
    word_count = len(words)

    if not words:
        top_word, top_count = "-", 0
    else:
        counter = Counter(words)
        # Most frequent; ties broken alphabetically (earliest wins).
        top_word, top_count = sorted(counter.items(), key=lambda x: (-x[1], x[0]))[0]

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
