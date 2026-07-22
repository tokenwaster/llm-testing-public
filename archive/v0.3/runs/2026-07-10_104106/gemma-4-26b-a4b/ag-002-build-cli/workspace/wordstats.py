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
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Count lines
    # "as split by newline; a trailing final newline does not add an extra line"
    if not content:
        lines_count = 0
    else:
        # splitlines() handles the trailing newline correctly for our needs
        lines_count = len(content.splitlines())

    # Extract words
    # A word is a maximal run of ASCII letters (a-z) after lowercasing.
    # Digits, punctuation and underscores separate words.
    lower_content = content.lower()
    # Replace everything that's not a-z with space
    words_only = re.sub(r'[^a-z]', ' ', lower_content)
    words = words_only.split()

    if not words:
        print(f"lines: {lines_count}")
        print(f"words: 0")
        print("top: - 0")
        return

    word_counts = Counter(words)
    total_words = len(words)

    # Find top word. Ties are broken alphabetically (earliest wins).
    # We want max frequency, then min alphabetical order.
    # Sort by (-count, word)
    sorted_counts = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
    top_word, top_count = sorted_counts[0]

    print(f"lines: {lines_count}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
