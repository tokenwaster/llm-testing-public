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
    # Using splitlines() handles this correctly.
    line_count = len(text.splitlines())

    # Lowercase the whole text, then find maximal runs of ASCII letters.
    lowered = text.lower()
    words = re.findall(r'[a-z]+', lowered)

    counter = Counter(words)

    if counter:
        # Most frequent; ties broken alphabetically (earliest wins).
        # Counter.most_common breaks ties by insertion order, not alphabetically,
        # so we sort explicitly.
        top_word, top_count = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
