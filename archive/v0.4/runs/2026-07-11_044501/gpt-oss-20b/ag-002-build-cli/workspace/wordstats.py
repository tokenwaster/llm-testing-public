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

    # Count lines (split by newline; trailing newline does not add an extra line)
    lines = len(text.splitlines())

    # Find words: maximal runs of ASCII letters after lowercasing
    words = re.findall(r'[a-z]+', text.lower())
    word_count = len(words)

    if words:
        counter = Counter(words)
        max_count = max(counter.values())
        # Get all words with max count, sort alphabetically, pick first
        top_words = [w for w,c in counter.items() if c==max_count]
        top_word = sorted(top_words)[0]
    else:
        top_word = '-'
        max_count = 0

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {max_count}")

if __name__ == "__main__":
    main()
