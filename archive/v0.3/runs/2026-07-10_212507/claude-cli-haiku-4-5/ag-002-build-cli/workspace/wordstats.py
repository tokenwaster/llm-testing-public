import sys
import re
from collections import Counter

def wordstats(filepath):
    with open(filepath, 'r') as f:
        text = f.read()

    # Count lines
    lines = len(text.splitlines()) if text else 0

    # Extract words (maximal runs of ASCII letters, lowercase)
    words = re.findall(r'[a-z]+', text.lower())

    # Count total words
    word_count = len(words)

    # Find top word
    if words:
        counter = Counter(words)
        # Sort by count (descending), then alphabetically for ties
        top_word, top_count = sorted(counter.items(), key=lambda x: (-x[1], x[0]))[0]
        print(f"lines: {lines}")
        print(f"words: {word_count}")
        print(f"top: {top_word} {top_count}")
    else:
        print(f"lines: {lines}")
        print(f"words: {word_count}")
        print("top: - 0")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    wordstats(sys.argv[1])
