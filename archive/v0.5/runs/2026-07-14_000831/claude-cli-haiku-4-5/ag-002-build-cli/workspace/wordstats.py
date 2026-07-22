import sys
import re
from collections import Counter

def wordstats(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Count lines (trailing newline doesn't add an extra line)
    lines = len(content.splitlines())

    # Extract words: lowercase text, find maximal runs of a-z
    text_lower = content.lower()
    words = re.findall(r'[a-z]+', text_lower)
    word_count = len(words)

    # Find most frequent word (alphabetical tie-breaking)
    if words:
        word_freq = Counter(words)
        # Sort by count (descending), then alphabetically (ascending)
        most_common = sorted(word_freq.items(), key=lambda x: (-x[1], x[0]))[0]
        top_word, top_count = most_common
    else:
        top_word, top_count = '-', 0

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    wordstats(sys.argv[1])
