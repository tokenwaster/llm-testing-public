#!/usr/bin/env python3
"""wordstats.py - print line count, word count, and most-frequent word."""

import re
import sys
from collections import Counter

WORD_RE = re.compile(r'[a-z]+')


def analyze(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # splitlines() handles the "trailing newline doesn't add an extra line"
    # convention correctly: "a\nb\n" -> ['a', 'b'] (2 lines), "" -> [] (0),
    # "\n" -> [''] (1 line).
    lines = len(text.splitlines())

    # Lowercase first, then extract maximal runs of ASCII letters.
    words = WORD_RE.findall(text.lower())
    total = len(words)

    counts = Counter(words)
    if counts:
        # Highest count wins; ties broken alphabetically (earliest).
        top_word = min(counts, key=lambda w: (-counts[w], w))
        top_count = counts[top_word]
    else:
        top_word = '-'
        top_count = 0

    print(f'lines: {lines}')
    print(f'words: {total}')
    print(f'top: {top_word} {top_count}')


def main(argv):
    if len(argv) != 2:
        print(f'Usage: {argv[0]} <path-to-text-file>', file=sys.stderr)
        return 1
    analyze(argv[1])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
