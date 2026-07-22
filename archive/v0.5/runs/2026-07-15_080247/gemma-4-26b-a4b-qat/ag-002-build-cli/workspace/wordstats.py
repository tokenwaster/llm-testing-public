import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Count lines
    # splitlines() handles the trailing newline requirement correctly
    lines = len(content.splitlines())

    # Extract words
    # A word is a maximal run of ASCII letters (a-z) after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    # Find top word
    if word_count == 0:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Sort by count descending, then by word ascending
        # We want the highest count, and for ties, the lexicographically smallest word.
        # To use sort() easily: sort by (-count, word)
        sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_counts[0]

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
