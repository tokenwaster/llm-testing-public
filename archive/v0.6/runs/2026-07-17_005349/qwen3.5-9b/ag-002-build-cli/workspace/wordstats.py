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
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    # Count lines - split by newline, trailing newline doesn't add extra line
    if text == '':
        num_lines = 0
    elif text.endswith('\n'):
        num_lines = text[:-1].split('\n', 1)[0].count('\n') + 1
        # Actually simpler: count newlines in the content without trailing one
        num_lines = text.count('\n')
    else:
        num_lines = text.count('\n') + 1
    
    # Process words
    # Lowercase the whole text
    text_lower = text.lower()
    
    # A word is a maximal run of ASCII letters (a-z)
    # Digits, punctuation and underscores separate words
    words = re.findall(r'[a-z]+', text_lower)
    
    if not words:
        print(f"lines: {num_lines}")
        print("words: 0")
        print("top: - 0")
    else:
        # Count word frequencies
        counter = Counter(words)
        
        # Find max count
        max_count = max(counter.values())
        
        # Get all words with max count, sort alphabetically, take first
        top_words = sorted([word for word, count in counter.items() if count == max_count])
        top_word = top_words[0]
        
        print(f"lines: {num_lines}")
        print(f"words: {len(words)}")
        print(f"top: {top_word} {max_count}")

if __name__ == "__main__":
    main()
