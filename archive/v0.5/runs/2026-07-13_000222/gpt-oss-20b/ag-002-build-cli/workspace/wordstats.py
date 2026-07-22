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
        print(f"Error reading file: {e}")
        sys.exit(1)
    # Count lines
    # splitlines() splits on any newline and does not include trailing empty line if ends with newline
    lines = len(text.splitlines())
    # Lowercase entire text
    lower_text = text.lower()
    # Find words: maximal runs of a-z
    words = re.findall(r"[a-z]+", lower_text)
    word_count = len(words)
    if word_count == 0:
        top_word, top_cnt = '-', 0
    else:
        counter = Counter(words)
        maxcnt = max(counter.values())
        # get all words with maxcnt, choose alphabetically earliest
        candidates = [w for w,c in counter.items() if c==maxcnt]
        top_word = min(candidates)
        top_cnt = maxcnt
    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_cnt}")

if __name__ == "__main__":
    main()
