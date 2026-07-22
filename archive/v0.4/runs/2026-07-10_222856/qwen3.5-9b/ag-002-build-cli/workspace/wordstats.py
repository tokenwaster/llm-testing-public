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
    
    # Count lines - split by newline; trailing final newline does not add extra line
    if content.endswith('\n'):
        lines = len(content.split('\n')) - 1
    else:
        lines = len(content.split('\n'))
    
    # Lowercase the text
    lower_content = content.lower()
    
    # Extract words - maximal run of ASCII letters a-z
    # Digits, punctuation and underscores separate words
    words = re.findall(r'[a-z]+', lower_content)
    
    # Count word frequencies
    if words:
        counter = Counter(words)
        # Find max count
        max_count = max(counter.values())
        # Get all words with max count
        top_words = [word for word, count in counter.items() if count == max_count]
        # Sort alphabetically and take the first one (earliest wins)
        top_words.sort()
        top_word = top_words[0]
    else:
        top_word = '-'
        top_count = 0
    
    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
