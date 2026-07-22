import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    with open(path, 'r') as f:
        content = f.read()

    # Count lines: split by newline; trailing final newline does not add extra line
    lines = content.split('\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]
    line_count = len(lines)

    # Lowercase the text
    lower_content = content.lower()

    # Find words: maximal runs of ASCII letters (a-z)
    words = re.findall(r'[a-z]+', lower_content)
    word_count = len(words)

    # Find top word
    if word_count == 0:
        top_word = '-'
        top_count = 0
    else:
        counter = Counter(words)
        # Ties broken alphabetically (earliest wins)
        top_word = min(counter.keys(), key=lambda w: (-counter[w], w))
        top_count = counter[top_word]

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == '__main__':
    main()
