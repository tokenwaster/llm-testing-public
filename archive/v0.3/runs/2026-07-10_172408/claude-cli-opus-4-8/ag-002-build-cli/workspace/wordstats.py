import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    # Number of lines: split by newline; a trailing final newline does not
    # add an extra line.
    if text == "":
        lines = 0
    else:
        n = text.count("\n")
        lines = n if text.endswith("\n") else n + 1

    words = re.findall(r"[a-z]+", text.lower())
    word_count = len(words)

    print(f"lines: {lines}")
    print(f"words: {word_count}")

    if words:
        counts = Counter(words)
        # Most frequent; ties broken alphabetically (earliest wins).
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        print(f"top: {top_word} {top_count}")
    else:
        print("top: - 0")


if __name__ == "__main__":
    main()
