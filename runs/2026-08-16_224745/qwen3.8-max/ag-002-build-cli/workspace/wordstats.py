#!/usr/bin/env python3
"""wordstats: report line count, word count, and most frequent word of a text file.

Usage: python wordstats.py <path-to-text-file>

Output (exactly three lines):
    lines: <number of lines in the file>
    words: <total word count>
    top: <word> <count>

Definitions:
- A word is a maximal run of ASCII letters (a-z) after lowercasing the text.
  Digits, punctuation and underscores separate words.
- lines is the count of lines split by newline; a trailing final newline does
  not add an extra line.
- top is the most frequent word; ties are broken alphabetically (earliest
  wins). If there are no words, print "top: - 0".
"""

import re
import sys
from collections import Counter

WORD_RE = re.compile(r"[a-z]+")


def count_lines(text):
    """Count lines split by '\\n'; a single trailing newline adds no line."""
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    return len(parts)


def main(argv):
    if len(argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2

    path = argv[1]
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as exc:
        print("error: cannot read {}: {}".format(path, exc), file=sys.stderr)
        return 1

    line_count = count_lines(text)

    words = WORD_RE.findall(text.lower())
    word_count = len(words)

    if words:
        counts = Counter(words)
        # Highest count wins; ties broken alphabetically (smallest word first).
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        top_line = "top: {} {}".format(top_word, top_count)
    else:
        top_line = "top: - 0"

    print("lines: {}".format(line_count))
    print("words: {}".format(word_count))
    print(top_line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
