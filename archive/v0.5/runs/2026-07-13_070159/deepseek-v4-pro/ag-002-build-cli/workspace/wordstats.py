import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Count lines: split by newline; trailing final newline does not add a line
    lines = text.splitlines()
    line_count = len(lines)

    # Count words: maximal runs of ASCII letters after lowercasing
    lower_text = text.lower()
    words = re.findall(r'[a-z]+', lower_text)
    word_count = len(words)

    # Most frequent word; ties broken alphabetically (earliest wins)
    if words:
        counter = Counter(words)
        # Sort by count descending, then alphabetically ascending
        top_word, top_count = min(counter.items(), key=lambda x: (-x[1], x[0]))
    else:
        top_word, top_count = '-', 0

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()