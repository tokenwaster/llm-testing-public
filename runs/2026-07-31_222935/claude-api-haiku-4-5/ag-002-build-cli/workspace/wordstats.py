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
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Count lines
    lines = content.count('\n')
    if content and not content.endswith('\n'):
        lines += 1
    
    # Extract words (maximal runs of ASCII letters after lowercasing)
    text_lower = content.lower()
    words = re.findall(r'[a-z]+', text_lower)
    
    # Count words
    word_count = len(words)
    
    # Find the top word
    if words:
        word_counter = Counter(words)
        # Sort by count (descending) then alphabetically (ascending)
        # Use min() because the negative count makes higher counts smaller
        top_word, top_count = min(word_counter.items(), key=lambda x: (-x[1], x[0]))
    else:
        top_word = '-'
        top_count = 0
    
    # Output the results
    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
