#!/usr/bin/env python3
"""wordstats.py — print line count, word count, and most frequent word.

Usage: python wordstats.py <path-to-text-file>
"""

import re
import sys
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Lines: split on '\n'; a trailing final newline does not add a line.
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    n_lines = len(parts)

    # Words: maximal runs of ASCII letters after lowercasing the whole text.
    words = re.findall(r"[a-z]+", text.lower())
    n_words = len(words)

    if words:
        counts = Counter(words)
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        top_line = "top: {} {}".format(top_word, top_count)
    else:
        top_line = "top: - 0"

    print("lines: {}".format(n_lines))
    print("words: {}".format(n_words))
    print(top_line)


if __name__ == "__main__":
    main()
