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
            lines = f.read().splitlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    line_count = len(lines)
    text = '\n'.join(lines).lower()
    words = re.findall(r'[a-z]+', text)
    word_count = len(words)
    if words:
        counter = Counter(words)
        max_freq = max(counter.values())
        top_words = [w for w, c in counter.items() if c == max_freq]
        top_word = min(top_words)  # alphabetically earliest
        top_count = max_freq
    else:
        top_word = '-'
        top_count = 0
    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
