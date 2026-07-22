#!/usr/bin/env python3
import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python wordstats.py <path-to-text-file>\n")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Lines: split by newline; trailing final newline does not add extra line.
    if text == "":
        lines = 0
    else:
        lines = text.count("\n")
        if not text.endswith("\n"):
            lines += 1

    # Words: maximal runs of ASCII letters after lowercasing.
    lowered = text.lower()
    words = re.findall(r"[a-z]+", lowered)

    if words:
        counter = Counter(words)
        # Most frequent; ties broken alphabetically (earliest wins).
        top_word, top_count = min(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
