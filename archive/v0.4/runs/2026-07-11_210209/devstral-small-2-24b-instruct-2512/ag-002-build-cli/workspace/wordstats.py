#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    
    # Count lines (trailing newline doesn't add an extra line)
    lines = len(content.split('\n')) - (content.endswith('\n') == False and content != '')
    if content == '':
        lines = 0
    
    # Extract words: maximal runs of ASCII letters after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    
    # Count word frequencies
    word_counts = defaultdict(int)
    for word in words:
        word_counts[word] += 1
    
    total_words = len(words)
    
    # Find top word (ties broken alphabetically)
    if not word_counts:
        print("lines: 0")
        print("words: 0")
        print("top: - 0")
        return
    
    max_count = max(word_counts.values())
    top_words = [word for word, count in word_counts.items() if count == max_count]
    top_word = min(top_words)  # alphabetically earliest
    
    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {max_count}")

if __name__ == "__main__":
    main()
