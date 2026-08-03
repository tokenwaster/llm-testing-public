import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: file '{path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Count lines: split by newline; a trailing newline does not add an extra line
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    line_count = len(lines)

    # Extract words: maximal runs of ASCII letters after lowercasing
    words = re.findall(r'[a-z]+', text.lower())
    word_count = len(words)

    # Find top word; ties broken alphabetically (earliest wins)
    if words:
        counts = Counter(words)
        # Sort by (-count, word) so highest count comes first, ties broken by word
        top_word, top_count = min(counts.items(), key=lambda x: (-x[1], x[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
