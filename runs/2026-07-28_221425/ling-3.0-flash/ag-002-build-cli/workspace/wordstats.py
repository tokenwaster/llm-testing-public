import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, 'r') as f:
        text = f.read()

    # Count lines: split by newline, trailing newline doesn't add extra line
    if text == '':
        line_count = 0
    else:
        line_count = len(text.split('\n'))
        # If text ends with newline, the last split element is empty, so subtract 1
        if text.endswith('\n'):
            line_count -= 1

    # Lowercase the whole text, then find words (maximal runs of ASCII letters a-z)
    lower_text = text.lower()
    words = re.findall(r'[a-z]+', lower_text)

    word_count = len(words)

    if words:
        counter = Counter(words)
        # Sort by (-count, word) to get highest count first, then alphabetical tiebreak
        top_word, top_count = sorted(counter.items(), key=lambda x: (-x[1], x[0]))[0]
        print(f"lines: {line_count}")
        print(f"words: {word_count}")
        print(f"top: {top_word} {top_count}")
    else:
        print(f"lines: {line_count}")
        print(f"words: {word_count}")
        print("top: - 0")

if __name__ == '__main__':
    main()
