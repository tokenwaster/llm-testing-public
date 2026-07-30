#!/usr/bin/env python3
"""wordstats.py - print line count, word count, and top word of a text file."""
import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Line count: split on newline; a trailing newline doesn't add a line.
    parts = content.split("\n")
    if parts and parts[-1] == "":
        parts = parts[:-1]
    num_lines = len(parts)

    # Words: maximal runs of ASCII letters on the lowercased text.
    text = content.lower()
    words = re.findall(r"[a-z]+", text)
    num_words = len(words)

    # Top word by count, ties broken alphabetically (earliest wins).
    if not words:
        top_word, top_count = "-", 0
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        # Pick the alphabetically smallest word among those with max count.
        top_word = min(w for w, c in counter.items() if c == max_count)
        top_count = max_count

    print(f"lines: {num_lines}")
    print(f"words: {num_words}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()