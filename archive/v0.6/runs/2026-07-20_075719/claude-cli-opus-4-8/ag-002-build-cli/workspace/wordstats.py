import re
import sys
from collections import Counter


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(2)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    # Line count: split on newline, ignore a single trailing newline.
    if text == "":
        line_count = 0
    else:
        line_count = text.count("\n") + (0 if text.endswith("\n") else 1)

    words = re.findall(r"[a-z]+", text.lower())
    word_count = len(words)

    print(f"lines: {line_count}")
    print(f"words: {word_count}")

    if words:
        counts = Counter(words)
        # Most frequent; ties broken alphabetically (earliest wins).
        word, count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        print(f"top: {word} {count}")
    else:
        print("top: - 0")


if __name__ == "__main__":
    main()
