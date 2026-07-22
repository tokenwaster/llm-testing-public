import re
import sys
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(2)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    # Line count: split on newline; a trailing final newline does not add a line.
    if text == "":
        line_count = 0
    else:
        line_count = text.count("\n")
        if not text.endswith("\n"):
            line_count += 1

    words = re.findall(r"[a-z]+", text.lower())
    word_count = len(words)

    print(f"lines: {line_count}")
    print(f"words: {word_count}")

    if not words:
        print("top: - 0")
    else:
        counts = Counter(words)
        # Most frequent; ties broken alphabetically (earliest wins).
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
