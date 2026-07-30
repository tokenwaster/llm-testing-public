#!/usr/bin/env python3
import sys
import re


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # splitlines(): trailing final newline does not add an extra line
    lines = len(text.splitlines())

    lower = text.lower()
    words = re.findall(r"[a-z]+", lower)

    print(f"lines: {lines}")
    print(f"words: {len(words)}")

    if not words:
        print("top: - 0")
        return

    counts: dict[str, int] = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1

    # Most frequent; ties broken alphabetically (earliest wins)
    top_word = min(counts.keys(), key=lambda w: (-counts[w], w))
    print(f"top: {top_word} {counts[top_word]}")


if __name__ == "__main__":
    main()
