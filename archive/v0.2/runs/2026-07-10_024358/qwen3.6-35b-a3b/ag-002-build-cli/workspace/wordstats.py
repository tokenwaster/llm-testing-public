#!/usr/bin/env python3
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, 'r') as f:
        content = f.read()

    # Count lines: split by newline, remove trailing empty string if file ends with \n
    lines = content.split('\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]
    line_count = len(lines)

    # Count words: lowercase, find maximal runs of ASCII letters
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    # Find top word
    if words:
        counter = Counter(words)
        max_count = max(counter.values())
        # Among words with max count, pick alphabetically first
        top_word = min(w for w, c in counter.items() if c == max_count)
        print(f"top: {top_word} {max_count}")
    else:
        print("top: - 0")

    print(f"lines: {line_count}")
    print(f"words: {word_count}")

if __name__ == '__main__':
    main()
