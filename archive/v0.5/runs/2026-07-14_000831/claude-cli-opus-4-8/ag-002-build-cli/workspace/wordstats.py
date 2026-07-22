#!/usr/bin/env python3
"""Print line count, word count, and the most frequent word of a text file.

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

    # Line count: number of newline-separated lines, ignoring a single
    # trailing newline. An empty file counts as 0 lines.
    if text == "":
        line_count = 0
    else:
        line_count = text.count("\n")
        if not text.endswith("\n"):
            line_count += 1

    words = WORD_RE.findall(text.lower())
    word_count = len(words)

    print(f"lines: {line_count}")
    print(f"words: {word_count}")

    if not words:
        print("top: - 0")
    else:
        counts = Counter(words)
        # Ties broken alphabetically: sort by (-count, word), take first.
        top_word, top_n = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        print(f"top: {top_word} {top_n}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
