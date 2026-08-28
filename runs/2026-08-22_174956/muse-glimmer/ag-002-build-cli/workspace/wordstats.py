#!/usr/bin/env python3
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Count lines as split by newline; trailing final newline does not add extra line
    lines = len(text.splitlines())

    # Lowercase whole text, then find maximal runs of ASCII letters
    lower = text.lower()
    words = re.findall(r'[a-z]+', lower)
    total_words = len(words)

    if total_words == 0:
        top_word = '-'
        top_count = 0
    else:
        counter = Counter(words)
        # Find most frequent with alphabetical tie-break
        # max with key = (count, -? Actually we want highest count, then smallest word)
        # Use sorted
        # Find max count first
        max_count = max(counter.values())
        # candidates with max_count
        candidates = [w for w, c in counter.items() if c == max_count]
        top_word = min(candidates)  # alphabetical earliest
        top_count = max_count

    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
