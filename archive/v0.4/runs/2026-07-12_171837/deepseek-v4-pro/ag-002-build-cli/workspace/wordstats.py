import re
import sys
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()
    num_lines = len(lines)

    words = re.findall(r"[a-z]+", text.lower())
    num_words = len(words)

    if not words:
        print(f"lines: {num_lines}")
        print(f"words: {num_words}")
        print("top: - 0")
        return

    counts = Counter(words)
    # most_common returns list of (word, count) sorted by count desc,
    # and for ties, by order of first appearance (which Counter preserves).
    # But we need alphabetical tie-breaking: earliest alphabetically wins.
    # So we need to sort by (-count, word) and take the first.
    top_word, top_count = min(counts.items(), key=lambda x: (-x[1], x[0]))

    print(f"lines: {num_lines}")
    print(f"words: {num_words}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
