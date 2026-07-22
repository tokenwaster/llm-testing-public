import sys
import re
from collections import Counter


def wordstats(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Count lines (split by newline, trailing newline doesn't add extra line)
    lines = len(content.splitlines())

    # Extract words: maximal runs of ASCII letters [a-z] after lowercasing
    lowercased = content.lower()
    words = re.findall(r'[a-z]+', lowercased)

    # Count total words
    word_count = len(words)

    # Find most frequent word (ties broken alphabetically)
    if words:
        word_freq = Counter(words)
        top_word, top_count = sorted(word_freq.items(), key=lambda x: (-x[1], x[0]))[0]
    else:
        top_word, top_count = '-', 0

    # Print results
    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        wordstats(filepath)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
