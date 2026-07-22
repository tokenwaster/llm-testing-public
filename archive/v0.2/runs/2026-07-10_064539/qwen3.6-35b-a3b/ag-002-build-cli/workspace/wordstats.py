import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, 'r') as f:
        content = f.read()

    # Count lines: trailing final newline does not add an extra line
    if content == '':
        line_count = 0
    elif content.endswith('\n'):
        line_count = content.count('\n')
    else:
        line_count = content.count('\n') + 1

    # Lowercase the text
    lower_content = content.lower()

    # Extract words: maximal runs of ASCII letters (a-z)
    words = re.findall(r'[a-z]+', lower_content)

    word_count = len(words)

    # Find top word
    if word_count == 0:
        top_word = '-'
        top_count = 0
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        top_words = [w for w, c in counter.items() if c == max_count]
        top_word = sorted(top_words)[0]
        top_count = max_count

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == '__main__':
    main()
