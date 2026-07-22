#!/usr/bin/env python3
import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        content = f.read()

    # Count lines: split by newline, but trailing final newline does not add an extra line.
    parts = content.split('\n')
    if parts and parts[-1] == '':
        parts.pop()
    line_count = len(parts)

    # Words: maximal runs of ASCII letters after lowercasing.
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    # Top word by frequency, ties broken alphabetically (earliest wins).
    if not words:
        top_line = "top: - 0"
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        candidates = sorted(w for w, c in counter.items() if c == max_count)
        top_word = candidates[0]
        top_line = f"top: {top_word} {max_count}"

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(top_line)


if __name__ == "__main__":
    main()
