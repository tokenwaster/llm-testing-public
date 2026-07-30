#!/usr/bin/env python3
import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        text = f.read()

    # Count lines — trailing final newline does not add an extra line.
    if text == "":
        line_count = 0
    else:
        if text.endswith("\n"):
            line_count = len(text.split("\n")) - 1
        else:
            line_count = len(text.split("\n"))

    # Words are maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", text.lower())
    word_count = len(words)

    print(f"lines: {line_count}")
    print(f"words: {word_count}")

    if words:
        counter = Counter(words)
        max_count = max(counter.values())
        top_words = sorted(w for w, c in counter.items() if c == max_count)
        print(f"top: {top_words[0]} {max_count}")
    else:
        print("top: - 0")


if __name__ == "__main__":
    main()
