import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Count lines: splitlines handles trailing newline correctly
    lines = content.splitlines()
    line_count = len(lines)

    # Normalize and extract words
    lower_text = content.lower()
    words = re.findall(r'[a-z]+', lower_text)
    word_count = len(words)

    if word_count == 0:
        top_word = '-'
        top_count = 0
    else:
        counter = Counter(words)
        # Sort by frequency (desc), then alphabetically (asc)
        sorted_items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_items[0]

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
