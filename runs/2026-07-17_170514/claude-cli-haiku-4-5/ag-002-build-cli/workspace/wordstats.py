import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Count lines (splitlines handles trailing newlines correctly)
    lines = len(text.splitlines())

    # Extract words: maximal runs of ASCII letters (a-z after lowercasing)
    text_lower = text.lower()
    words = re.findall(r'[a-z]+', text_lower)

    word_count = len(words)

    # Find the most frequent word (ties broken alphabetically)
    if words:
        counter = Counter(words)
        top_word = sorted(counter.items(), key=lambda x: (-x[1], x[0]))[0]
        print(f"lines: {lines}")
        print(f"words: {word_count}")
        print(f"top: {top_word[0]} {top_word[1]}")
    else:
        print(f"lines: {lines}")
        print(f"words: {word_count}")
        print(f"top: - 0")

if __name__ == "__main__":
    main()
