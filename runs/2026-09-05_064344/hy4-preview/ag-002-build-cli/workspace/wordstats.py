#!/usr/bin/env python3
"""wordstats.py - print line count, word count and most frequent word of a text file.

Usage: python wordstats.py <path-to-text-file>
"""

import re
import sys

WORD_RE = re.compile(r"[a-z]+")


def count_lines(text):
    """Number of lines in text; a trailing final newline does not add a line."""
    if text == "":
        return 0
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return len(lines)


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

    lowered = text.lower()
    words = WORD_RE.findall(lowered)

    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1

    if counts:
        # highest count first, then alphabetically smallest word
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        top_word, top_count = "-", 0

    sys.stdout.write("lines: %d\n" % count_lines(text))
    sys.stdout.write("words: %d\n" % len(words))
    sys.stdout.write("top: %s %d\n" % (top_word, top_count))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
