#!/usr/bin/env python3
"""Print line count, word count, and most frequent word of a text file.

Usage: python wordstats.py <path-to-text-file>
"""
import re
import sys
from collections import Counter

WORD_RE = re.compile(r"[a-z]+")


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: python wordstats.py <path-to-text-file>\n")
        return 2

    with open(argv[1], "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Line count: number of newline-separated lines, with a trailing final
    # newline not adding an extra empty line. An empty file has 0 lines.
    if text == "":
        lines = 0
    else:
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)

    words = WORD_RE.findall(text.lower())
    total_words = len(words)

    if words:
        counts = Counter(words)
        # Most frequent; ties broken alphabetically (earliest wins).
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        top_word, top_count = "-", 0

    sys.stdout.write(f"lines: {lines}\n")
    sys.stdout.write(f"words: {total_words}\n")
    sys.stdout.write(f"top: {top_word} {top_count}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
