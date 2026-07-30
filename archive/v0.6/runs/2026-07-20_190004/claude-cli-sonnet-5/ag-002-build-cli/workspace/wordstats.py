#!/usr/bin/env python3
import re
import sys


def main():
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if text == "":
        lines = 0
    else:
        lines = text.count("\n")
        if not text.endswith("\n"):
            lines += 1

    words = re.findall(r"[a-z]+", text.lower())

    print(f"lines: {lines}")
    print(f"words: {len(words)}")

    if not words:
        print("top: - 0")
        return

    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1

    top_word = min(counts, key=lambda w: (-counts[w], w))
    print(f"top: {top_word} {counts[top_word]}")


if __name__ == "__main__":
    main()
