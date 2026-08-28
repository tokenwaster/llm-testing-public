import sys
import re
from collections import Counter

def wordstats(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Count lines
    lines = len(content.splitlines())

    # Extract words (lowercase, then find all maximal runs of a-z)
    text_lower = content.lower()
    words = re.findall(r'[a-z]+', text_lower)
    word_count = len(words)

    # Find top word
    if words:
        word_freq = Counter(words)
        # Sort by count (descending), then by word (ascending for alphabetical)
        top_word, top_count = min(word_freq.items(), key=lambda x: (-x[1], x[0]))
    else:
        top_word, top_count = '-', 0

    # Output
    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
    wordstats(sys.argv[1])
