#!/usr/bin/env python3
import sys
import re

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    with open(filepath, 'r') as f:
        text = f.read()
    
    # Count lines (trailing newline doesn't add extra line)
    if len(text) == 0:
        lines = 0
    elif text[-1] == '\n':
        lines = len(text.rstrip('\n').split('\n'))
    else:
        lines = len(text.split('\n'))
    
    # Extract words (maximal runs of ASCII letters after lowercasing)
    lowered = text.lower()
    words = re.findall(r'[a-z]+', lowered)
    
    total_words = len(words)
    
    # Find most frequent word, ties broken alphabetically
    if not words:
        print("lines:", lines)
        print("words:", total_words)
        print("top: - 0")
        return
    
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    max_count = max(word_counts.values())
    # Get all words with max count and sort alphabetically (earliest wins)
    top_words = sorted([w for w, c in word_counts.items() if c == max_count])
    top_word = top_words[0]
    
    print("lines:", lines)
    print("words:", total_words)
    print(f"top: {top_word} {max_count}")

if __name__ == "__main__":
    main()