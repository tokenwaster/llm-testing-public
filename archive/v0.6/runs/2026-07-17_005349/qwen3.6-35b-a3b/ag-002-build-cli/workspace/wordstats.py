#!/usr/bin/env python3
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Count lines: splitlines handles trailing newline correctly
    lines = content.splitlines()
    line_count = len(lines)

    # Find words: maximal runs of ASCII letters after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    # Find top word
    if word_count == 0:
        top_word = "-"
        top_count = 0
    else:
        counter = Counter(words)
        # Find max count, then among ties pick alphabetically earliest
        max_count = max(counter.values())
        candidates = [w for w, c in counter.items() if c == max_count]
        top_word = min(candidates)  # alphabetically earliest
        top_count = max_count

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
