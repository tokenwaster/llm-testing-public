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
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    # Count lines
    # A trailing final newline does not add an extra line
    if content == '':
        lines = 0
    elif content.endswith('\n'):
        lines = content.count('\n')
    else:
        lines = content.count('\n') + 1
    
    # Lowercase the whole text
    text_lower = content.lower()
    
    # Extract words: maximal runs of ASCII letters (a-z)
    words = re.findall(r'[a-z]+', text_lower)
    
    # Count word frequencies
    if not words:
        top_word = '-'
        top_count = 0
    else:
        word_counts = Counter(words)
        max_count = max(word_counts.values())
        top_words = [word for word, count in word_counts.items() if count == max_count]
        top_words.sort()  # Alphabetically sort (earliest wins on ties)
        top_word = top_words[0]
        top_count = max_count
    
    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
