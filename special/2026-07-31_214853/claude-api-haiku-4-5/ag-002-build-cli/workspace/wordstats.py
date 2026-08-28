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
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Count lines: split by newline, but don't count a trailing final newline as an extra line
    lines = content.splitlines()
    line_count = len(lines) if lines or content == "" else 0
    # Handle edge case: empty file has 0 lines
    if content == "":
        line_count = 0
    else:
        line_count = len(content.splitlines())
    
    # Extract words: lowercase and find all maximal runs of ASCII letters
    content_lower = content.lower()
    words = re.findall(r'[a-z]+', content_lower)
    
    # Count words
    word_count = len(words)
    
    # Find top word
    if word_count == 0:
        top_word = "-"
        top_count = 0
    else:
        word_counter = Counter(words)
        # Sort by count (descending) then by word (ascending) for ties
        top_word, top_count = sorted(word_counter.items(), key=lambda x: (-x[1], x[0]))[0]
    
    # Print results
    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
