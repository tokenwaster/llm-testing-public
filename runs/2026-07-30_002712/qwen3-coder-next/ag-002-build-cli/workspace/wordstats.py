#!/usr/bin/env python3
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    with open(filepath, 'r', encoding='ascii') as f:
        content = f.read()
    
    # Count lines (split by newline; trailing newline doesn't add extra line)
    if content == '':
        num_lines = 0
    else:
        num_lines = len(content.split('\n'))
        # If file ends with newline, don't count the empty string after last newline as a line
        if content.endswith('\n'):
            num_lines -= 1
    
    # Extract words: maximal runs of ASCII letters after lowercasing
    text_lower = content.lower()
    words = re.findall(r'[a-z]+', text_lower)
    
    word_count = len(words)
    
    if word_count == 0:
        top_word = '-'
        top_count = 0
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        # Get all words with max count, then sort alphabetically
        top_words = sorted([w for w, c in counter.items() if c == max_count])
        top_word = top_words[0]
        top_count = max_count
    
    print(f"lines: {num_lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
