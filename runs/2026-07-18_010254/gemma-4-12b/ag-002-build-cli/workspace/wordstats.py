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
    line_count = len(lines)

    # Extract words
    # A word is a maximal run of ASCII letters (a-z) after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    # Find top word
    if not words:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Sort by count descending, then alphabetically ascending
        sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_words[0]

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
