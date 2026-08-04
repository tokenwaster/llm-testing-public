#!/usr/bin/env python3
"""Print simple word statistics for a text file.

Usage: python wordstats.py <path-to-text-file>

Output (exactly three lines):
    lines: <number of lines in the file>
    words: <total word count>
    top: <word> <count>
"""

import re
import sys
from collections import Counter

WORD_RE = re.compile(r"[a-z]+")


def count_lines(text: str) -> int:
    """Number of lines, where a trailing final newline adds no extra line."""
    if not text:
        return 0
    n = text.count("\n")
    if not text.endswith("\n"):
        n += 1
    return n


def stats(text: str):
    lowered = text.lower()
    words = WORD_RE.findall(lowered)
    counts = Counter(words)
    if counts:
        # Most frequent; ties broken alphabetically (earliest wins).
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        top_word, top_count = "-", 0
    return count_lines(text), len(words), top_word, top_count


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: python wordstats.py <path-to-text-file>\n")
        return 2
    path = argv[1]
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        sys.stderr.write("error: cannot read %s: %s\n" % (path, exc))
        return 1

    n_lines, n_words, top_word, top_count = stats(text)
    sys.stdout.write("lines: %d\n" % n_lines)
    sys.stdout.write("words: %d\n" % n_words)
    sys.stdout.write("top: %s %d\n" % (top_word, top_count))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
