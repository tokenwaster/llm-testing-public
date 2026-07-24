#!/usr/bin/env python3
import re
import sys
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Lines: split by newline; a trailing final newline does not add an extra line.
    parts = content.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    lines = len(parts)

    # Words: maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", content.lower())
    word_count = len(words)

    # Top word: most frequent, ties broken alphabetically (earliest wins).
    if words:
        counts = Counter(words)
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
