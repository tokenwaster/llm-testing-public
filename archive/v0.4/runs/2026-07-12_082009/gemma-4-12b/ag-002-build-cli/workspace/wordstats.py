import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        return

    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return

    # Count lines
    # splitlines() handles \n, \r\n and doesn't count trailing newline as extra line
    lines_list = content.splitlines()
    num_lines = len(lines_list)

    # Extract words (maximal runs of ASCII letters after lowercasing)
    words = re.findall(r'[a-z]+', content.lower())
    num_words = len(words)

    # Count frequencies
    counts = Counter(words)

    if not words:
        top_word = "-"
        top_count = 0
    else:
        # Sort by count descending, then alphabetically ascending
        # sorted() is stable, but we can just use a custom key.
        # We want max count (negative for descending) and min word (alphabetical).
        sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_items[0]

    print(f"lines: {num_lines}")
    print(f"words: {num_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
