#!/usr/bin/env python3
"""
Command-line tool that prints statistics about a text file.
Usage: python wordstats.py <path-to-text-file>
Outputs:
  lines: <number of lines>
  words: <total number of words>
  top: <word> <count>
"""
import sys
from collections import Counter
import re


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"File not found: {path}")
        sys.exit(1)

    # Count lines (split by newline; trailing newline does not add an extra line)
    lines = text.splitlines()
    num_lines = len(lines)

    # Lowercase entire text for word extraction
    lowered = text.lower()
    words_list = re.findall(r"[a-z]+", lowered)
    total_words = len(words_list)

    if words_list:
        counter = Counter(words_list)
        max_count = max(counter.values())
        # Get all words with max count, choose alphabetically first
        top_word = min([w for w, c in counter.items() if c == max_count])
    else:
        top_word = "-"
        max_count = 0

    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {max_count}")

if __name__ == "__main__":
    main()
