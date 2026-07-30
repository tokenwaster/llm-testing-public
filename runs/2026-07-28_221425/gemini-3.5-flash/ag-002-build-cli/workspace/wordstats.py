#!/usr/bin/env python3
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Calculate lines
    # A trailing final newline does not add an extra line.
    if not content:
        lines = 0
    else:
        if content.endswith('\n'):
            lines = content.count('\n')
        else:
            lines = content.count('\n') + 1

    # Extract words
    # A word is a maximal run of ASCII letters (a-z) after lowercasing the whole text.
    words = re.findall(r'[a-z]+', content.lower())
    
    total_words = len(words)
    
    # Calculate top word
    counts = Counter(words)
    if not counts:
        top_word = "-"
        top_count = 0
    else:
        # Tie break alphabetically (earliest wins).
        # min finds the item with the smallest key.
        # Key: (-count, word) -> largest count first, then alphabetical word first.
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))

    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
