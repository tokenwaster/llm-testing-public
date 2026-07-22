import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        return

    file_path = sys.argv[1]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return

    # Count lines
    lines = content.splitlines()
    num_lines = len(lines)

    # Extract words
    # A word is a maximal run of ASCII letters (a-z) after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    total_words = len(words)

    # Count frequencies
    counts = Counter(words)

    # Find top word
    if not counts:
        top_word = "-"
        top_count = 0
    else:
        # Sort by count descending, then alphabetically ascending
        sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_items[0]

    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
