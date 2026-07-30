#!/usr/bin/env python3
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    with open(filepath, 'r') as f:
        text = f.read()

    # Count lines
    if text == '':
        num_lines = 0
    elif text.endswith('\n'):
        num_lines = text.count('\n')
    else:
        num_lines = text.count('\n') + 1

    # Extract words: lowercase, then find maximal runs of ASCII letters
    words = re.findall(r'[a-z]+', text.lower())
    num_words = len(words)

    # Find top word
    if num_words == 0:
        top_word = '-'
        top_count = 0
    else:
        freq = Counter(words)
        max_count = max(freq.values())
        # Among words with max_count, pick alphabetically first
        candidates = [w for w, c in freq.items() if c == max_count]
        candidates.sort()
        top_word = candidates[0]
        top_count = max_count

    print(f"lines: {num_lines}")
    print(f"words: {num_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
