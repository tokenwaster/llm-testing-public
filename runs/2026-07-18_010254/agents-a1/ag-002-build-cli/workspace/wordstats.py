#!/usr/bin/env python3
import sys
from collections import defaultdict

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    filepath = sys.argv[1]

    # Read file content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count lines - handle trailing newline correctly
    # Strip trailing newlines before splitting to avoid extra empty line
    line_count = len(content.rstrip('\n').split('\n'))

    # Extract words: lowercase, then find maximal runs of ASCII letters (a-z)
    content_lower = content.lower()
    words = []
    current_word = []
    for char in content_lower:
        if 'a' <= char <= 'z':
            current_word.append(char)
        else:
            if current_word:
                words.append(''.join(current_word))
                current_word = []
    if current_word:
        words.append(''.join(current_word))

    # Count word frequencies
    word_counts = defaultdict(int)
    for word in words:
        word_counts[word] += 1

    total_words = len(words)

    # Find top word with alphabetical tie-breaking
    if word_counts:
        # Sort by count descending, then by word ascending
        sorted_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_words[0]
    else:
        top_word = '-'
        top_count = 0

    print(f"lines: {line_count}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
