#!/usr/bin/env python3
"""wordstats.py - count lines, words, and most frequent word in a text file."""
import sys
import re
from collections import Counter


def count_lines(text):
    """Count lines: split by newline; a trailing final newline adds no line.

    An empty file has 0 lines.
    """
    if text == "":
        return 0
    parts = text.split("\n")
    # If the file ends with a newline, the final split element is the empty
    # string and does not represent an extra line.
    if parts[-1] == "":
        parts = parts[:-1]
    return len(parts)


def extract_words(text):
    """Return list of words: maximal runs of ASCII letters a-z after lowercasing."""
    return re.findall(r"[a-z]+", text.lower())


def top_word(words):
    """Return (word, count) for the most frequent word, ties broken alphabetically.

    If `words` is empty, return ("-", 0).
    """
    if not words:
        return "-", 0
    counts = Counter(words)
    # Sort by descending count, then ascending word for tie-break.
    best_word, best_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return best_word, best_count


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = count_lines(text)
    words = extract_words(text)
    word_count = len(words)
    top, top_count = top_word(words)

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top} {top_count}")


if __name__ == "__main__":
    main()
