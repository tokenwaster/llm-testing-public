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

    lines = text.split("\n")
    line_count = len(lines) - 1 if text.endswith("\n") else len(lines)

    lowered = text.lower()
    words = re.findall(r"[a-z]+", lowered)
    word_count = len(words)

    if words:
        counts = Counter(words)
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
