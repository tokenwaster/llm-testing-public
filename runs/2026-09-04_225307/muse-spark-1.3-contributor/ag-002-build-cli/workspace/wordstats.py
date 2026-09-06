#!/usr/bin/env python3
import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # lines: number of lines as split by newline;
    # trailing final newline does not add extra line.
    # Empty file -> 0 lines.
    if text == "":
        n_lines = 0
    else:
        n_lines = text.count("\n") + (0 if text.endswith("\n") else 1)

    lowered = text.lower()
    words = re.findall(r'[a-z]+', lowered)
    n_words = len(words)

    if not words:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        max_count = max(counts.values())
        # ties broken alphabetically (earliest wins)
        candidates = [w for w, c in counts.items() if c == max_count]
        top_word = min(candidates)
        top_count = max_count

    sys.stdout.write(f"lines: {n_lines}\n")
    sys.stdout.write(f"words: {n_words}\n")
    sys.stdout.write(f"top: {top_word} {top_count}\n")

if __name__ == "__main__":
    main()
