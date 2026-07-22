#!/usr/bin/env python3
import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, 'r') as f:
        content = f.read()

    # Count lines: trailing newline does not add an extra line.
    if not content:
        lines = 0
    elif content.endswith('\n'):
        lines = content.count('\n')
    else:
        lines = content.count('\n') + 1

    # Extract words (maximal runs of ASCII letters after lowercasing)
    words = re.findall(r'[a-z]+', content.lower())

    if not words:
        print(f"lines: {lines}")
        print("words: 0")
        print("top: - 0")
    else:
        counter = Counter(words)
        # Most frequent word; ties broken alphabetically (earliest wins)
        top_word, top_count = sorted(counter.items(), key=lambda x: (-x[1], x[0]))[0]
        print(f"lines: {lines}")
        print(f"words: {len(words)}")
        print(f"top: {top_word} {top_count}")


if __name__ == '__main__':
    main()
