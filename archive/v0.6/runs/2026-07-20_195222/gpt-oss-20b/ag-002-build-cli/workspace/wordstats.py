#!/usr/bin/env python3
import sys
import os
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
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Count lines
    # splitlines() removes trailing newline and does not count it as empty line
    lines = text.splitlines()
    num_lines = len(lines)

    # Process words
    lower_text = text.lower()
    words = []
    current = []
    for ch in lower_text:
        if 'a' <= ch <= 'z':
            current.append(ch)
        else:
            if current:
                words.append(''.join(current))
                current = []
    if current:
        words.append(''.join(current))

    word_count = len(words)
    counter = Counter(words)
    if counter:
        max_count = max(counter.values())
        # get all words with max count, sort alphabetically
        top_words = [w for w,c in counter.items() if c==max_count]
        top_word = sorted(top_words)[0]
    else:
        top_word = '-'
        max_count = 0

    print(f"lines: {num_lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {max_count}")

if __name__ == "__main__":
    main()
