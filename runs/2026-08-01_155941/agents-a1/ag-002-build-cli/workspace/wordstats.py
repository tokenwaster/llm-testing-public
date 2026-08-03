#!/usr/bin/env python3
import sys
from collections import Counter
import re

def main():
    if len(sys.argv) < 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Count lines using splitlines (handles \n, \r\n; ignores trailing final newline)
    line_count = len(text.splitlines())

    lower_text = text.lower()
    words = re.findall(r'[a-z]+', lower_text)
    total_words = len(words)

    if total_words == 0:
        top_line = "top: - 0"
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        candidates = [w for w, c in counter.items() if c == max_count]
        # Tie-breaking: alphabetical (earliest wins) -> min(candidates) uses default string order
        top_word = min(candidates)
        top_line = f"top: {top_word} {max_count}"

    print(f"lines: {line_count}")
    print(f"words: {total_words}")
    print(top_line)

if __name__ == "__main__":
    main()