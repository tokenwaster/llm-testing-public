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
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Count lines (split by newline, trailing newline doesn't add extra line)
    if content == '':
        lines = 0
    else:
        lines = len(content.split('\n'))
    
    # Lowercase the content
    lower_content = content.lower()
    
    # Extract words: maximal runs of ASCII letters a-z
    words = re.findall(r'[a-z]+', lower_content)
    
    # Total word count
    word_count = len(words)
    
    # Find most frequent word
    if word_count == 0:
        top_word = '-'
        top_count = 0
    else:
        counter = Counter(words)
        # Get the most common, ties broken alphabetically
        # Sort by (-count, word) to get highest count first, then alphabetically
        sorted_words = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_words[0]
    
    # Print output
    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()