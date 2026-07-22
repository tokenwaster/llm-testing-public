#!/usr/bin/env python3
"""Command-line tool to compute word statistics from a text file."""

import sys
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        content = f.read()

    # Count lines: split by newline; trailing final newline does not add an extra line.
    parts = content.split("\n")
    if len(parts) > 0 and parts[-1] == "":
        num_lines = len(parts) - 1
    else:
        num_lines = len(parts)

    # Lowercase the whole text, then find words as maximal runs of ASCII letters.
    lower = content.lower()
    words = []
    current_word = []
    for ch in lower:
        if "a" <= ch <= "z":
            current_word.append(ch)
        else:
            if current_word:
                words.append("".join(current_word))
                current_word = []
    # Flush any trailing word
    if current_word:
        words.append("".join(current_word))

    total_words = len(words)

    # Find top word (most frequent, ties broken alphabetically)
    if not words:
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print("top: - 0")
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        # Among all words with max_count, pick the alphabetically first one
        top_word = min(w for w, c in counter.items() if c == max_count)
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print(f"top: {top_word} {max_count}")


if __name__ == "__main__":
    main()
