#!/usr/bin/env python3
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
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Count lines
    lines = len(text.splitlines())

    # Find words (ASCII letters only, lowercased)
    words = re.findall(r'[a-z]+', text.lower())
    word_count = len(words)

    if words:
        counter = Counter(words)
        max_count = max(counter.values())
        top_words = [w for w, c in counter.items() if c == max_count]
        top_word = min(top_words)  # alphabetically earliest
        print(f"lines: {lines}")
        print(f"words: {word_count}")
        print(f"top: {top_word} {max_count}")
    else:
        print(f"lines: {lines}")
        print("words: 0")
        print("top: - 0")

if __name__ == "__main__":
    main()
