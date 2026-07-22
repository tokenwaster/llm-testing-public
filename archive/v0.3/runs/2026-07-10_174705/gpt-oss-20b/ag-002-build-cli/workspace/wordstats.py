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
    except FileNotFoundError:
        print(f"File not found: {path}")
        sys.exit(1)
    # Count lines
    lines = text.splitlines()
    num_lines = len(lines)
    # Lowercase entire text for word extraction
    lower_text = text.lower()
    words_list = re.findall(r'[a-z]+', lower_text)
    total_words = len(words_list)
    counter = Counter(words_list)
    if counter:
        max_count = max(counter.values())
        # Get all words with max count
        top_candidates = [w for w, c in counter.items() if c == max_count]
        top_word = min(top_candidates)  # alphabetically earliest
        top_info = f"{top_word} {max_count}"
    else:
        top_info = "- 0"
    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(f"top: {top_info}")

if __name__ == '__main__':
    main()
