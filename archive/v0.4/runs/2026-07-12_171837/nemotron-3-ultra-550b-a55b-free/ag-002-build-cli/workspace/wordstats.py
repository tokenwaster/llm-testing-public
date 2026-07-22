#!/usr/bin/env python3
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Count lines (split by newline, trailing newline doesn't add extra line)
    lines = content.split('\n')
    # If the file ends with a newline, the last element will be empty string
    # We don't count that as an extra line
    if lines and lines[-1] == '':
        line_count = len(lines) - 1
    else:
        line_count = len(lines)

    # Extract words: maximal runs of ASCII letters after lowercasing
    # Lowercase the whole text first
    lower_content = content.lower()
    # Find all runs of a-z
    words = re.findall(r'[a-z]+', lower_content)

    word_count = len(words)

    # Find most frequent word
    if words:
        counter = Counter(words)
        # Get max count
        max_count = max(counter.values())
        # Get all words with max count, sort alphabetically, pick first
        top_words = [w for w, c in counter.items() if c == max_count]
        top_word = min(top_words)  # alphabetically earliest
        top_count = max_count
    else:
        top_word = '-'
        top_count = 0

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()