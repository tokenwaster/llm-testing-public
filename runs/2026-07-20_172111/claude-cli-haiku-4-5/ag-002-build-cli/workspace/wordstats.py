#!/usr/bin/env python3
import sys
import re
from collections import Counter

def wordstats(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count lines: split by newline and don't count trailing newline as extra
    if content.endswith('\n'):
        lines = len(content.rstrip('\n').split('\n')) if content.rstrip('\n') else 1
    else:
        lines = len(content.split('\n')) if content else 1

    # Extract words: maximal runs of ASCII letters, lowercased
    # Replace non-letter characters with spaces to separate words
    text_lower = content.lower()
    words = re.findall(r'[a-z]+', text_lower)

    word_count = len(words)

    # Find most frequent word with alphabetical tie-breaking
    if words:
        counter = Counter(words)
        # Sort by count (descending) then alphabetically
        most_common = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = most_common[0]
    else:
        top_word, top_count = '-', 0

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
    wordstats(sys.argv[1])
