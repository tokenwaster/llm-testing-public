#!/usr/bin/env python3
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count lines: split by newline, trailing final newline does not add extra line
    if content == '':
        line_count = 0
    else:
        parts = content.split('\n')
        if content.endswith('\n'):
            line_count = len(parts) - 1
        else:
            line_count = len(parts)

    # Extract words: maximal runs of ASCII letters after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    # Find top word
    if word_count == 0:
        top_line = "top: - 0"
    else:
        counter = Counter(words)
        # Find max count, then among ties pick alphabetically earliest
        max_count = max(counter.values())
        top_words = [w for w, c in counter.items() if c == max_count]
        top_word = min(top_words)  # alphabetically earliest
        top_line = f"top: {top_word} {max_count}"

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(top_line)

if __name__ == '__main__':
    main()
