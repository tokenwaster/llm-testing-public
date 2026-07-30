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
    except Exception:
        return

    # Count lines
    # "lines is the number of lines in the file (as split by newline; a trailing final newline does not add an extra line)."
    if not content:
        num_lines = 0
    else:
        lines_split = content.split('\n')
        # If the last element is empty and there was a preceding character, 
        # it means there was a trailing newline.
        if len(lines_split) > 1 and lines_split[-1] == '':
            num_lines = len(lines_split) - 1
        else:
            num_lines = len(lines_split)

    # Count words
    # A word is a maximal run of ASCII letters (a-z) after lowercasing.
    words = re.findall(r'[a-zA-Z]+', content)
    words = [w.lower() for w in words]
    total_words = len(words)

    if not words:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Sort by frequency descending, then by word alphabetically ascending
        sorted_counts = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        top_word, top_count = sorted_counts[0]

    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
