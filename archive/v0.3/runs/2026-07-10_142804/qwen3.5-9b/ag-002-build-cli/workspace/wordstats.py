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
    
    # Count lines - split by newline, trailing newline doesn't add extra line
    if content == '':
        lines = 0
    else:
        lines = content.count('\n')
        if content[-1] != '\n':
            lines += 1
    
    # Lowercase the text
    text_lower = content.lower()
    
    # Extract words (maximal runs of ASCII letters a-z)
    words = re.findall(r'[a-z]+', text_lower)
    
    # Count word frequencies
    if words:
        word_counts = Counter(words)
        # Find max count
        max_count = max(word_counts.values())
        # Get all words with max count
        top_words = [word for word, count in word_counts.items() if count == max_count]
        # Sort alphabetically and take first (earliest wins)
        top_word = sorted(top_words)[0]
        top_count = max_count
    else:
        top_word = '-'
        top_count = 0
    
    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
