#!/usr/bin/env python3

import re

def wordstats(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Find all words (max 1 to 26 letters)
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    if not words:
        print(f"top: - 0")
        return
    
    line_count = len(text.splitlines()) + 1  # +1 for empty file case
    word_counts = {}
    for w in words:
        word_counts[w] = word_counts.get(w, 0) + 1
    
    top_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))[:3]
    print(f"lines: {line_count}")
    print(f"words: {sum(word_counts.values())}")
    for w, count in top_words:
        print(f"top: {w} {count}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    wordstats(filename))
