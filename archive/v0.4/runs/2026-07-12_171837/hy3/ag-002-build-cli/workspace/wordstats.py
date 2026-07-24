#!/usr/bin/env python3
import re
import sys
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Number of lines, split by newline; a trailing final newline does not
    # add an extra line.
    if content == "":
        lines = 0
    else:
        lines = content.count("\n")
        if not content.endswith("\n"):
            lines += 1

    # Words: maximal runs of ASCII letters after lowercasing.
    words = re.findall(r"[a-z]+", content.lower())

    total_words = len(words)

    if total_words == 0:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Most frequent; ties broken alphabetically (earliest wins).
        top_word, top_count = min(
            counts.items(), key=lambda kv: (-kv[1], kv[0])
        )

    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
