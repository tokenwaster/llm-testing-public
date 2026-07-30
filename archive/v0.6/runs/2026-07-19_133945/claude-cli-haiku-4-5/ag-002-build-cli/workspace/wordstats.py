import sys
import re
from collections import Counter

def wordstats(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Count lines: newline count, +1 if content exists and doesn't end with newline
    if not content:
        lines = 0
    else:
        lines = content.count('\n')
        if not content.endswith('\n'):
            lines += 1

    # Extract words: maximal runs of lowercase ASCII letters
    text_lower = content.lower()
    words = re.findall(r'[a-z]+', text_lower)

    # Count total words
    total_words = len(words)

    # Find top word: break ties alphabetically (earliest wins)
    if words:
        word_counts = Counter(words)
        top_word, top_count = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))[0]
        print(f"lines: {lines}")
        print(f"words: {total_words}")
        print(f"top: {top_word} {top_count}")
    else:
        print(f"lines: {lines}")
        print(f"words: {total_words}")
        print("top: - 0")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
    wordstats(sys.argv[1])
