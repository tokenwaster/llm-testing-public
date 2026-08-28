#!/usr/bin/env python3
"""wordstats.py -- report basic statistics about a text file.

Usage:
    python wordstats.py <path-to-text-file>

Prints exactly three lines to stdout:

    lines: <number of lines in the file>
    words: <total word count>
    top: <word> <count>

Definitions used:
  * A "word" is a maximal run of ASCII letters (a-z) taken from the
    lowercased text.  Digits, punctuation, underscores and any other
    characters act as separators.
  * "lines" counts lines as split by '\\n'; a trailing final newline does
    not add an extra (empty) line.
  * "top" is the most frequent word; ties are broken alphabetically
    (earliest word wins).  With no words at all, "top: - 0" is printed.
"""

import re
import sys
from collections import Counter

_WORD_RE = re.compile(r"[a-z]+")


def read_text(path):
    """Read *path* and return its contents as text.

    UTF-8 is preferred; if the bytes are not valid UTF-8, Latin-1 is used as
    a lossless fallback (every byte decodes, and non-ASCII bytes are never
    ASCII letters, so word/line counting is unaffected).
    """
    with open(path, "rb") as handle:
        data = handle.read()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def count_lines(text):
    """Number of lines when splitting on newline.

    A trailing final newline does not produce an extra empty line.  An empty
    text has zero lines.
    """
    if text == "":
        return 0
    parts = text.split("\n")
    if parts[-1] == "":
        parts.pop()
    return len(parts)


def find_words(text):
    """All words (maximal runs of a-z) in the lowercased text, in order."""
    return _WORD_RE.findall(text.lower())


def top_word(counts):
    """(word, count) of the most frequent word; ties broken alphabetically."""
    # Sort key: highest count first, then alphabetically earliest word.
    return min(counts.items(), key=lambda item: (-item[1], item[0]))


def main(argv):
    if len(argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2

    path = argv[1]
    try:
        text = read_text(path)
    except OSError as exc:
        print("wordstats: cannot read {}: {}".format(path, exc), file=sys.stderr)
        return 1

    words = find_words(text)
    counts = Counter(words)

    if counts:
        best_word, best_count = top_word(counts)
    else:
        best_word, best_count = "-", 0

    print("lines: {}".format(count_lines(text)))
    print("words: {}".format(len(words)))
    print("top: {} {}".format(best_word, best_count))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
