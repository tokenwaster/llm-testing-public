#!/usr/bin/env python3
"""Command-line tool to compute basic word statistics of a text file.

Usage: python wordstats.py <path-to-text-file>

Prints three lines:
    lines: <number of lines in the file>
    words: <total word count>
    top: <word> <count>
"""

import re
import sys
from collections import Counter


def count_lines(content: str) -> int:
    """Count lines split by newline; a trailing final newline adds no extra line."""
    parts = content.split('\n')
    # A trailing newline produces a trailing empty string element that
    # does not represent an actual line.
    if parts and parts[-1] == '':
        parts.pop()
    return len(parts)


def extract_words(content: str) -> list:
    """Return all words: maximal runs of ASCII letters a-z after lowercasing."""
    return re.findall(r'[a-z]+', content.lower())


def top_word(words: list):
    """Return (word, count) for the most frequent word.

    Ties are broken alphabetically (earliest wins).
    Returns ('-', 0) when there are no words.
    """
    if not words:
        return '-', 0
    counter = Counter(words)
    max_count = max(counter.values())
    best = min(w for w, c in counter.items() if c == max_count)
    return best, max_count


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    num_lines = count_lines(content)
    words = extract_words(content)
    num_words = len(words)
    word, count = top_word(words)

    print(f"lines: {num_lines}")
    print(f"words: {num_words}")
    print(f"top: {word} {count}")


if __name__ == '__main__':
    main()
