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
    # Count lines
    # splitlines handles various newline conventions and does not count a trailing newline as extra line
    line_count = len(text.splitlines())
    # Process words
    lowered = text.lower()
    words = re.findall(r'[a-z]+', lowered)
    word_count = len(words)
    if word_count == 0:
        top_word = '-'
        top_count = 0
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        # Get all words with max_count and pick alphabetically smallest
        candidates = [w for w, c in counter.items() if c == max_count]
        top_word = min(candidates)
        top_count = max_count
    # Output
    print(f'lines: {line_count}')
    print(f'words: {word_count}')
    print(f'top: {top_word} {top_count}')

if __name__ == '__main__':
    main()
