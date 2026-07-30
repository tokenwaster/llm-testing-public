#!/usr/bin/env python3
import sys
import re
from collections import Counter


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: python wordstats.py <path-to-text-file>\n")
        return 1

    path = argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # A line is determined by splitting on newlines; a trailing final newline
    # does not add an extra line.
    lines = len(text.splitlines())

    # A word is a maximal run of ASCII letters (a-z) after lowercasing.
    words = re.findall(r"[a-z]+", text.lower())
    word_count = len(words)

    if words:
        counts = Counter(words)
        # Most frequent; ties broken alphabetically (earliest wins).
        top_word, top_count = min(
            counts.items(), key=lambda kv: (-kv[1], kv[0])
        )
    else:
        top_word, top_count = "-", 0

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
