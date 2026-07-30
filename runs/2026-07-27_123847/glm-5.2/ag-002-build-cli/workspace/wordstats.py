#!/usr/bin/env python3
import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python wordstats.py <path-to-text-file>\n")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Lines: split by newline; trailing final newline does not add extra line.
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    line_count = len(lines)

    # Words: maximal runs of ASCII letters after lowercasing.
    lower_text = text.lower()
    words = re.findall(r"[a-z]+", lower_text)
    word_count = len(words)

    # Top word: most frequent, ties broken alphabetically.
    if words:
        counter = Counter(words)
        top_word = min(counter.items(), key=lambda kv: (-kv[1], kv[0]))
        top_line = "top: {} {}".format(top_word[0], top_word[1])
    else:
        top_line = "top: - 0"

    print("lines: {}".format(line_count))
    print("words: {}".format(word_count))
    print(top_line)


if __name__ == "__main__":
    main()
