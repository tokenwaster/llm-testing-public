import sys
import re
from collections import Counter


def count_lines(content: str) -> int:
    """Count lines: split by newline, strip trailing empty element if present."""
    parts = content.split('\n')
    # A trailing newline adds an empty string at the end; remove it.
    if len(parts) > 0 and parts[-1] == '':
        parts = parts[:-1]
    return len(parts)


def extract_words(content: str):
    """Extract all words from content after lowercasing."""
    text = content.lower()
    # A word is a maximal run of ASCII letters (a-z).
    return re.findall(r'[a-z]+', text)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()

    line_count = count_lines(content)
    words = extract_words(content)
    word_count = len(words)

    print(f"lines: {line_count}")
    print(f"words: {word_count}")

    if word_count == 0:
        print("top: - 0")
    else:
        counter = Counter(words)
        # Most common gives (word, count). For ties, we need the alphabetically earliest.
        # Counter.most_common() doesn't guarantee tie-breaking order reliably across versions,
        # so let's do it explicitly.
        max_count = max(counter.values())
        candidates = [w for w, c in counter.items() if c == max_count]
        top_word = sorted(candidates)[0]
        print(f"top: {top_word} {max_count}")


if __name__ == '__main__':
    main()
