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
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Count lines - trailing final newline does not add an extra line
    if text.endswith('\n'):
        lines = text[:-1].split('\n')
    else:
        lines = text.split('\n')
    
    num_lines = len(lines)
    
    # Lowercase the whole text
    text_lower = text.lower()
    
    # Extract words: maximal run of ASCII letters (a-z)
    # Digits, punctuation and underscores separate words
    words = re.findall(r'[a-z]+', text_lower)
    
    total_words = len(words)
    
    if total_words == 0:
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print("top: - 0")
    else:
        # Count word frequencies
        word_counts = Counter(words)
        
        # Find the most frequent word, with ties broken alphabetically
        max_count = max(word_counts.values())
        top_words = [word for word, count in word_counts.items() if count == max_count]
        top_word = sorted(top_words)[0]  # Alphabetically first
        
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print(f"top: {top_word} {max_count}")

if __name__ == "__main__":
    main()
