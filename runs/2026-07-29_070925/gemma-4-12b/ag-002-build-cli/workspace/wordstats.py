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

    # Count lines: a trailing final newline does not add an extra line.
    lines = content.splitlines()
    line_count = len(lines)

    # Extract words: maximal run of ASCII letters (a-z) after lowercasing.
    lower_content = content.lower()
    words = re.findall(r'[a-z]+', lower_content)
    word_count = len(words)

    # Count word frequencies.
    counts = Counter(words)

    # Find the top word (max frequency, then alphabetical tiebreaker).
    if not counts:
        top_line = "top: - 0"
    else:
        # Sort by count descending (-x[1]) and then alphabetically (x[0]).
        sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        best_word, best_count = sorted_words[0]
        top_line = f"top: {best_word} {best_count}"

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(top_line)

if __name__ == "__main__":
    main()
