import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        text = f.read()

    # Count lines (split by newline; trailing final newline does not add an extra line)
    if text == "":
        num_lines = 0
    elif text.endswith("\n"):
        num_lines = text.count("\n")
    else:
        num_lines = text.count("\n") + 1

    # Extract words: maximal runs of ASCII letters after lowercasing
    lowered = text.lower()
    words = re.findall(r"[a-z]+", lowered)

    counts = Counter(words)

    if not counts:
        print(f"lines: {num_lines}")
        print("words: 0")
        print("top: - 0")
    else:
        # Most frequent word; ties broken alphabetically (earliest wins)
        top_word, top_count = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[0]

        print(f"lines: {num_lines}")
        print(f"words: {len(words)}")
        print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
