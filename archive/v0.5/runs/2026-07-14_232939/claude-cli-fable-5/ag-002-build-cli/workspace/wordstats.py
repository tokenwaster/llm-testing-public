import re
import sys
from collections import Counter


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(2)

    with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Line count: splitting on newline; a trailing final newline adds no line.
    if text == "":
        line_count = 0
    else:
        line_count = text.count("\n") + (0 if text.endswith("\n") else 1)

    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)

    print(f"lines: {line_count}")
    print(f"words: {len(words)}")
    if counts:
        top_word = min(counts, key=lambda w: (-counts[w], w))
        print(f"top: {top_word} {counts[top_word]}")
    else:
        print("top: - 0")


if __name__ == "__main__":
    main()
