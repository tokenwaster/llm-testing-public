#!/usr/bin/env python3
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print('Usage: python wordstats.py <path-to-text-file>', file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f'Error reading file: {e}', file=sys.stderr)
        sys.exit(1)
    # Count lines using splitlines (does not count a trailing empty line)
    lines = text.splitlines()
    num_lines = len(lines)
    # Lowercase whole text
    lower = text.lower()
    # Find words: maximal runs of ASCII letters a-z
    words = re.findall(r'[a-z]+', lower)
    total_words = len(words)
    if total_words == 0:
        top_word = '-'
        top_count = 0
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        # Get all words with max_count and pick alphabetically earliest
        candidates = [w for w, c in counter.items() if c == max_count]
        top_word = min(candidates)
        top_count = max_count
    # Output
    print(f'lines: {num_lines}')
    print(f'words: {total_words}')
    print(f'top: {top_word} {top_count}')

if __name__ == "__main__":
    main()
