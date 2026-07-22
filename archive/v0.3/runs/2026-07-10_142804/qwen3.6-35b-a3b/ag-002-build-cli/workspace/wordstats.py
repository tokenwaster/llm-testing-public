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
        content = f.read()

    # Count lines
    if content == '':
        line_count = 0
    elif content.endswith('\n'):
        line_count = content.count('\n')
    else:
        line_count = content.count('\n') + 1

    # Extract words: maximal runs of ASCII letters after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    # Print lines and words first
    print(f"lines: {line_count}")
    print(f"words: {word_count}")

    # Find top word
    if words:
        counter = Counter(words)
        max_count = max(counter.values())
        # Among ties, pick alphabetically earliest
        top_word = min(w for w, c in counter.items() if c == max_count)
        print(f"top: {top_word} {max_count}")
    else:
        print("top: - 0")

if __name__ == '__main__':
    main()
