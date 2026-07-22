#!/usr/bin/env python3
import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    # Count lines: splitlines handles trailing newline correctly
    lines = len(text.splitlines()) if text else 0

    # Extract words: maximal runs of ASCII letters after lowercasing
    words = re.findall(r'[a-z]+', text.lower())
    word_count = len(words)

    # Find top word
    if word_count == 0:
        print(f"lines: {lines}")
        print(f"words: {word_count}")
        print("top: - 0")
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        # Among ties, pick alphabetically first (min of sorted candidates)
        top_word = min(w for w, c in counter.items() if c == max_count)
        print(f"lines: {lines}")
        print(f"words: {word_count}")
        print(f"top: {top_word} {max_count}")


if __name__ == "__main__":
    main()
