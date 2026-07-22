import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)

    # Line count
    # splitlines() handles the trailing newline requirement correctly.
    # If content is empty, it returns [], len 0.
    # "a\n".splitlines() -> ['a'], len 1.
    # "a\nb\n".splitlines() -> ['a', 'b'], len 2.
    lines = len(content.splitlines())

    # Word extraction
    # Lowercase first, then find all maximal runs of [a-z]
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    if not words:
        top_word, top_freq = "-", 0
    else:
        counts = Counter(words)
        # Sort by frequency descending, then alphabetically ascending
        sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_freq = sorted_items[0]

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_freq}")

if __name__ == "__main__":
    main()
