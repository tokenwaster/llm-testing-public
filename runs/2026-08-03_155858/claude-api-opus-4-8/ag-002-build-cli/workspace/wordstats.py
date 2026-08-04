import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    if text == "":
        lines = 0
    else:
        n = text.count("\n")
        lines = n if text.endswith("\n") else n + 1

    words = re.findall(r"[a-z]+", text.lower())
    total = len(words)

    if not words:
        print(f"lines: {lines}")
        print(f"words: {total}")
        print("top: - 0")
        return

    counts = Counter(words)
    best_word = min(counts, key=lambda w: (-counts[w], w))
    print(f"lines: {lines}")
    print(f"words: {total}")
    print(f"top: {best_word} {counts[best_word]}")


if __name__ == "__main__":
    main()
