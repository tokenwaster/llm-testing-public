#!/usr/bin/env python3
import sys
import re
from collections import Counter

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
    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Count lines using splitlines() which handles trailing newline correctly
    lines = len(content.splitlines())
    
    # Extract words: maximal run of ASCII letters (a-z) after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    
    total_words = len(words)
    
    if words:
        word_counts = Counter(words)
        # Sort by descending count, then ascending word for alphabetical tie-breaking
        sorted_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_words[0]
    else:
        top_word = "-"
        top_count = 0
    
    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
