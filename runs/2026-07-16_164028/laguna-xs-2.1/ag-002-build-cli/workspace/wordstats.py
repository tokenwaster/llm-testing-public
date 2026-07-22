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
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Count lines (split by newline, trailing newline doesn't add extra line)
    lines = len(text.splitlines())
    
    # Lowercase the text
    text_lower = text.lower()
    
    # Extract words: maximal runs of ASCII letters a-z
    words = re.findall(r'[a-z]+', text_lower)
    
    # Total word count
    word_count = len(words)
    
    # Find most frequent word
    if word_count == 0:
        print("lines:", lines)
        print("words:", word_count)
        print("top: - 0")
    else:
        counter = Counter(words)
        # Get the most common word(s)
        max_count = counter.most_common(1)[0][1]
        # Get all words with max count and sort alphabetically
        top_words = sorted([word for word, count in counter.items() if count == max_count])
        top_word = top_words[0]
        
        print("lines:", lines)
        print("words:", word_count)
        print("top:", top_word, max_count)

if __name__ == "__main__":
    main()