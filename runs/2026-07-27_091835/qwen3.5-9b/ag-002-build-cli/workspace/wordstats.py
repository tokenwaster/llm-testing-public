#!/usr/bin/env python3
import sys
import re


def count_lines(text):
    """Count lines in text, where trailing final newline doesn't add extra line."""
    if not text:
        return 0
    lines = text.split('\n')
    # If the last element is empty (due to trailing newline), don't count it
    if lines and lines[-1] == '':
        return len(lines) - 1
    else:
        return len(lines)


def get_words(text):
    """Extract words from text after lowercasing. Words are runs of a-z."""
    # Replace all non-letter characters with spaces, then find all a-z sequences
    cleaned = ' '.join(c if c.isalpha() and c.islower() or c.isupper() else ' ' for c in text.lower())
    return re.findall(r'[a-z]+', cleaned)


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Calculate line count
    num_lines = count_lines(content)
    
    # Extract words and count frequencies
    word_counts = {}
    for word in get_words(content):
        word_counts[word] = word_counts.get(word, 0) + 1
    
    total_words = sum(word_counts.values())
    
    # Find top word (most frequent, ties broken alphabetically - earliest wins)
    if not word_counts:
        top_word = '-'
        top_count = 0
    else:
        # Sort by count descending, then by word ascending for alphabetical tie-breaking
        sorted_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
        top_word = sorted_words[0][0]
        top_count = sorted_words[0][1]
    
    # Print results
    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")


if __name__ == '__main__':
    main()
