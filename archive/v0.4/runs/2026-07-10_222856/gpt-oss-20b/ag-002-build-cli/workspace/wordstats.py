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
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    # Count lines (trailing newline does not add an extra line)
    num_lines = len(lines)
    text = ''.join(lines).lower()
    words = re.findall(r'[a-z]+', text)
    total_words = len(words)
    if total_words == 0:
        top_word, top_count = '-', 0
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        # get all words with max count and choose alphabetically smallest
        candidates = [w for w,c in counter.items() if c==max_count]
        top_word = min(candidates)
        top_count = max_count
    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
