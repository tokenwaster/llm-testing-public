import re
import sys
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    words = re.findall(r"[a-z]+", text.lower())

    counts = Counter(words)
    if counts:
        max_count = max(counts.values())
        top_word = min(w for w, c in counts.items() if c == max_count)
        top_count = max_count
    else:
        top_word, top_count = "-", 0

    print(f"lines: {len(lines)}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
