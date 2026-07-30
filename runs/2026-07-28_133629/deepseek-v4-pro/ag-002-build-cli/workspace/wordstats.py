import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Count lines: split by newline; a trailing final newline does not add an extra line
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]
    line_count = len(lines)

    # Extract words: lowercase the whole text, then find all runs of ASCII letters
    lower_text = text.lower()
    words = re.findall(r'[a-z]+', lower_text)
    word_count = len(words)

    # Find most frequent word (tie-break alphabetically)
    if words:
        counter = Counter(words)
        # max over counter items: sort by (-count, word) and pick first
        top_word, top_count = min(counter.items(), key=lambda x: (-x[1], x[0]))
    else:
        top_word = '-'
        top_count = 0

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
