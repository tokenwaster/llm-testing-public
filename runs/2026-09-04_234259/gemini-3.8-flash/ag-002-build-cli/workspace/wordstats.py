import sys
import re
from collections import Counter


def count_lines(content: str) -> int:
    if not content:
        return 0
    if content.endswith('\n'):
        content = content[:-1]
    return len(content.split('\n'))


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    line_count = count_lines(content)

    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    if word_count == 0:
        top_str = "- 0"
    else:
        counts = Counter(words)
        # Highest count, then alphabetically earliest word
        top_word = min(counts.keys(), key=lambda w: (-counts[w], w))
        top_str = f"{top_word} {counts[top_word]}"

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_str}")


if __name__ == '__main__':
    main()
