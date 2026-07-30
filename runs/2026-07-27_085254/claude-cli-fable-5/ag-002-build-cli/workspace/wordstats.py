import re
import sys
from collections import Counter


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2
    with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    if text.endswith("\n"):
        line_count = text.count("\n")
    else:
        line_count = text.count("\n") + 1 if text else 0

    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)

    print(f"lines: {line_count}")
    print(f"words: {len(words)}")
    if counts:
        top_word = min(counts, key=lambda w: (-counts[w], w))
        print(f"top: {top_word} {counts[top_word]}")
    else:
        print("top: - 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
