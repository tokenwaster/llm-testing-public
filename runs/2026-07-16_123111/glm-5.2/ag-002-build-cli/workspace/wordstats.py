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

    # Lines: split by newline; trailing final newline does not add an extra line.
    # Using splitlines() handles this naturally (it doesn't produce a trailing empty string).
    lines = text.splitlines()
    line_count = len(lines)

    # Words: maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", text.lower())

    if words:
        counter = Counter(words)
        # Find the most frequent word; ties broken alphabetically (earliest wins).
        # Counter.most_common does not guarantee alphabetical tie-breaking,
        # so we sort by (-count, word) and pick the first.
        top_word, top_count = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
