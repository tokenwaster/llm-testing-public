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

    # Count lines: trailing newline does not add an extra line
    if content == '':
        num_lines = 0
    else:
        num_lines = content.count('\n') if content.endswith('\n') else content.count('\n') + 1

    # Find all words: maximal runs of ASCII letters after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    num_words = len(words)

    # Find the most frequent word; ties broken alphabetically (earliest wins)
    if num_words == 0:
        print(f"lines: {num_lines}")
        print(f"words: {num_words}")
        print("top: - 0")
    else:
        word_counts = Counter(words)
        # Sort by (-count, word) to get highest count first, then alphabetically
        top_word, top_count = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))[0]
        print(f"lines: {num_lines}")
        print(f"words: {num_words}")
        print(f"top: {top_word} {top_count}")


if __name__ == '__main__':
    main()
