#!/usr/bin/env python3
"""wordstats.py -- print line count, word count and most frequent word.

Usage: python wordstats.py <path-to-text-file>

Output (exactly three lines on stdout):
    lines: <number of lines in the file>
    words: <total word count>
    top: <word> <count>

A *word* is a maximal run of ASCII letters (a-z) after lowercasing the
whole text; digits, punctuation and underscores separate words.
Ties for `top` are broken alphabetically (earliest wins). If there are
no words at all, `top` is printed as "- 0".
"""

import re
import sys
from collections import Counter

WORD_RE = re.compile(r"[a-z]+")


def count_lines(text: str) -> int:
    """Number of lines when splitting on newline; a single trailing
    final newline does not add an extra line."""
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    return len(parts)


def analyze(text: str):
    """Return (n_lines, n_words, top_word_or_None, top_count)."""
    n_lines = count_lines(text)

    words = WORD_RE.findall(text.lower())
    n_words = len(words)

    if words:
        counts = Counter(words)
        # Highest count first, then alphabetical order.
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        top_word, top_count = None, 0

    return n_lines, n_words, top_word, top_count


def main(argv):
    if len(argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2

    path = argv[1]
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: cannot read '{path}': {exc}", file=sys.stderr)
        return 1

    n_lines, n_words, top_word, top_count = analyze(text)

    print(f"lines: {n_lines}")
    print(f"words: {n_words}")
    print(f"top: {top_word if top_word is not None else '-'} {top_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
