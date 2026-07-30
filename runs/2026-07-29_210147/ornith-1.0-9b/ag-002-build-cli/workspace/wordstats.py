#!/usr/bin/env python3
import sys
import re


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r") as f:
        text = f.read()

    # Count lines: split by newline; a trailing final newline does not add an extra line.
    if text.endswith("\n"):
        lines = len(text.split("\n")) - 1
    else:
        lines = len(text.split("\n"))

    # Words: maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", text.lower())

    if not words:
        print(f"lines: {lines}")
        print("words: 0")
        print("top: - 0")
        return

    # Count frequencies, break ties alphabetically (earliest wins).
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1

    top_word = min(counts, key=lambda w: (-counts[w], w))
    top_count = counts[top_word]

    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
