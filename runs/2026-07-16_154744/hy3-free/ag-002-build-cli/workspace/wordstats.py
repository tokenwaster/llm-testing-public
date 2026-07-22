import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Number of lines: split by newline; trailing newline doesn't add a line.
    lines = text.split("\n")
    num_lines = len(lines) - 1 if text.endswith("\n") else len(lines)
    if text == "":
        num_lines = 0

    # Lowercase and extract words (maximal runs of a-z).
    lower = text.lower()
    words = re.findall(r"[a-z]+", lower)

    word_count = len(words)
    counter = Counter(words)

    if counter:
        # Most frequent; ties broken alphabetically (earliest wins).
        top_word, top_count = min(
            counter.items(), key=lambda kv: (-kv[1], kv[0])
        )
    else:
        top_word, top_count = "-", 0

    print(f"lines: {num_lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
