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
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Count lines
    # "a trailing final newline does not add an extra line"
    # splitlines() handles this correctly. 
    # If content is empty, lines should be 0? Or 1? 
    # Usually, an empty file has 0 lines.
    if not content:
        lines_count = 0
    else:
        # We need to be careful with splitlines(). 
        # "a\n" -> ["a"] (1 line)
        # "a\nb" -> ["a", "b"] (2 lines)
        # "" -> [] (0 lines)
        # "\n" -> [""] (1 line? No, splitlines() on "\n" gives ['']) 
        # Wait, let's check.
        lines_count = len(content.splitlines())

    # Count words
    # A word is a maximal run of ASCII letters (a-z) after lowercasing.
    # Digits, punctuation and underscores separate words.
    lower_content = content.lower()
    # Replace everything that is not a-z with space
    words_only = re.sub(r'[^a-z]', ' ', lower_content)
    words = words_only.split()
    word_counts = Counter(words)
    total_words = len(words)

    # Find top word
    if not words:
        top_word = "-"
        top_count = 0
    else:
        # Sort by count (descending) and then by word (ascending)
        # To handle ties alphabetically, we can sort the items.
        # We want max count, then min word.
        # A common trick is to use (-count, word) as key for sorting.
        sorted_counts = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_counts[0]

    print(f"lines: {lines_count}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
