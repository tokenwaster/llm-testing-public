#!/usr/bin/env python3
import sys
import re

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
    if content == "":
        num_lines = 0
    else:
        # Split by newline - a trailing newline doesn't add an extra line
        num_lines = len(content.rstrip('\n').split('\n')) if content.rstrip('\n') else 0
    
    # Extract words: maximal runs of ASCII letters [a-z]
    # First lowercase the text
    text_lower = content.lower()
    
    # Find all maximal runs of letters
    words = re.findall(r'[a-z]+', text_lower)
    
    # Count words
    word_count = len(words)
    
    # Find the most frequent word
    if word_count == 0:
        top_word = "-"
        top_count = 0
    else:
        # Count word frequencies
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Find the word with maximum frequency
        # Break ties alphabetically (earliest wins)
        max_count = max(word_freq.values())
        candidates = [word for word, count in word_freq.items() if count == max_count]
        top_word = min(candidates)  # Alphabetically first
        top_count = max_count
    
    # Print output
    print(f"lines: {num_lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
