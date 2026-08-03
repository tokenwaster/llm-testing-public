#!/usr/bin/env python3
import sys
from collections import Counter
import re

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
    
    path = sys.argv[1]
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Count lines using splitlines() which handles trailing newline correctly
    line_count = len(content.splitlines())
    
    # Lowercase the whole text for word extraction
    lower_content = content.lower()
    
    # Extract words - maximal run of ASCII letters a-z (after lowercasing)
    words = re.findall(r'[a-z]+', lower_content)
    
    total_words = len(words)
    
    if total_words == 0:
        top_word = '-'
        top_count = 0
    else:
        # Count word frequencies
        counter = Counter(words)
        # Find max count
        max_count = max(counter.values())
        # Get all words with that count and sort alphabetically
        top_words = [word for word, count in counter.items() if count == max_count]
        top_word = min(top_words)  # earliest alphabetically wins
        top_count = max_count
    
    print(f"lines: {line_count}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
