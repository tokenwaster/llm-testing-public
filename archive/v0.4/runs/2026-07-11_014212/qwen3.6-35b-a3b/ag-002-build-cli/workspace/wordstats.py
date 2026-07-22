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

    # Count lines: split by newline, strip trailing empty element
    if content == '':
        line_count = 0
    else:
        lines = content.split('\n')
        if lines and lines[-1] == '':
            lines = lines[:-1]
        line_count = len(lines)

    # Find words: maximal runs of ASCII letters after lowercasing
    lower_content = content.lower()
    words = re.findall(r'[a-z]+', lower_content)
    word_count = len(words)

    # Find top word
    if word_count == 0:
        top_word = '-'
        top_count = 0
    else:
        counter = Counter(words)
        # Sort by (-count, word) to get highest count first, then alphabetically
        top_word, top_count = min(counter.items(), key=lambda item: (-item[1], item[0]))

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
