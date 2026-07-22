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
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Count lines
    lines = text.splitlines()
    num_lines = len(lines)

    # Find words (ASCII letters only, lowercased)
    words = re.findall(r'[a-z]+', text.lower())
    total_words = len(words)

    # Determine top word
    if words:
        counter = Counter(words)
        # Get items sorted by (-count, word) to break ties alphabetically
        top_word, top_count = min(counter.items(), key=lambda x: (-x[1], x[0]))
    else:
        top_word, top_count = '-', 0

    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
