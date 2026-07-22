import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Lines count
    # splitlines() handles the trailing newline correctly according to requirements
    lines = content.splitlines()
    num_lines = len(lines)
    # Special case for empty file: if content is "", lines should be 0.
    # If content is "\n", lines should be 1.
    # Actually, splitlines() on "" returns [].
    # Let's check the requirement again: "a trailing final newline does not add an extra line"
    # If file is empty, lines = 0.
    # If file is "\n", lines = 1.
    # Wait, if content is "\n", splitlines() returns ['']. len is 1. Correct.
    # Let's test this later.

    # Words count
    # A word is a maximal run of ASCII letters (a-z) after lowercasing.
    # Digits, punctuation and underscores separate words.
    lower_content = content.lower()
    words = re.findall(r'[a-z]+', lower_content)
    num_words = len(words)

    if num_words == 0:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Find the most frequent word. Ties broken alphabetically (earliest wins).
        # To handle ties, we can sort by (-count, word)
        sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_counts[0]

    print(f"lines: {num_lines}")
    print(f"words: {num_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
