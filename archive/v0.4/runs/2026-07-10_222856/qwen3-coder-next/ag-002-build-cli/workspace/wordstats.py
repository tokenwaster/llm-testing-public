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
        with open(filepath, 'r', encoding='ascii') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Count lines (split by newline; trailing newline doesn't add extra line)
    if content == '':
        num_lines = 0
    else:
        num_lines = len(content.split('\n'))
        # If the file ends with a newline, don't count an extra empty line
        if content.endswith('\n'):
            num_lines -= 1
    
    # Extract words: maximal runs of ASCII letters after lowercasing
    text_lower = content.lower()
    words = re.findall(r'[a-z]+', text_lower)
    
    word_count = len(words)
    
    # Find top word (most frequent, ties broken alphabetically)
    if words:
        counter = Counter(words)
        max_count = max(counter.values())
        # Get all words with max count and sort alphabetically
        top_words = [word for word, count in counter.items() if count == max_count]
        top_word = sorted(top_words)[0]
        top_count = max_count
    else:
        top_word = '-'
        top_count = 0
    
    print(f"lines: {num_lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
