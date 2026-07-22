import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        content = f.read()

    # Count lines: split by newline; trailing final newline does not add an extra line.
    if not content:
        line_count = 0
    else:
        parts = content.split("\n")
        if parts[-1] == "":
            parts = parts[:-1]
        line_count = len(parts)

    # Extract words: maximal runs of ASCII letters after lowercasing.
    lower_content = content.lower()
    words = re.findall(r"[a-z]+", lower_content)

    word_count = len(words)

    if word_count == 0:
        top_word = "-"
        top_count = 0
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        candidates = sorted(w for w, c in counter.items() if c == max_count)
        top_word = candidates[0]
        top_count = max_count

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
