#!/usr/bin/env python3
"""
Command-line tool that prints statistics about a text file.
Usage:
    python wordstats.py <path-to-text-file>
Outputs three lines:
    lines: <number of lines in the file>
    words: <total word count>
    top: <word> <count>

A *word* is defined as a maximal run of ASCII letters (a–z) after lowercasing the whole text.
Digits, punctuation and underscores separate words.
If there are no words, the third line will be "top: - 0".
"""
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"File not found: {path}")
        sys.exit(1)

    # Count lines (split by newline; trailing newline does not add an extra line)
    lines = len(text.splitlines())

    # Find words: maximal runs of ASCII letters a-z after lowercasing
    lowered = text.lower()
    words_list = re.findall(r"[a-z]+", lowered)
    word_count = len(words_list)

    if word_count == 0:
        top_word, top_cnt = '-', 0
    else:
        counter = Counter(words_list)
        max_cnt = max(counter.values())
        # Get all words with max count and pick alphabetically earliest
        candidates = [w for w, c in counter.items() if c == max_cnt]
        top_word = min(candidates)
        top_cnt = max_cnt

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_cnt}")

if __name__ == "__main__":
    main()
