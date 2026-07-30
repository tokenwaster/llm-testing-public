import sys
import re
from collections import Counter

def wordstats(filepath):
    with open(filepath, 'r') as f:
        text = f.read()

    # Count lines
    lines = len(text.splitlines())

    # Extract words (lowercase, only ASCII letters a-z)
    text_lower = text.lower()
    words_list = re.findall(r'[a-z]+', text_lower)

    total_words = len(words_list)

    # Find most frequent word
    if words_list:
        word_counts = Counter(words_list)
        max_count = max(word_counts.values())
        # Get all words with max count and sort alphabetically, take first
        top_word = min([w for w, c in word_counts.items() if c == max_count])

        print(f"lines: {lines}")
        print(f"words: {total_words}")
        print(f"top: {top_word} {max_count}")
    else:
        print(f"lines: {lines}")
        print(f"words: {total_words}")
        print(f"top: - 0")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    wordstats(sys.argv[1])
