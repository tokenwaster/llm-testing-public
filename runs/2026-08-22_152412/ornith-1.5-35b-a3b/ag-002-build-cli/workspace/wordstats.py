#!/usr/bin/env python3
"""Report line count, word count, and most frequent word of a text file."""

import re
import sys
from collections import Counter


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: python wordstats.py <path-to-text-file>\n")
        return 2

    path = argv[1]
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Lines: split by newline; a trailing final newline does not add a line.
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    num_lines = len(parts)

    # Words: maximal runs of ASCII letters after lowercasing the whole text.
    words = re.findall(r"[a-z]+", text.lower())
    num_words = len(words)

    if words:
        counts = Counter(words)
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        print("top: %s %d" % (top_word, top_count))
    else:
        print("top: - 0")

    print("lines: %d" % num_lines)
    print("words: %d" % num_words)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
