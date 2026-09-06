import re
import sys
from collections import Counter

WORD_RE = re.compile(r"[a-z]+")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return 2
    with open(sys.argv[1], "r", encoding="utf-8", errors="replace", newline="") as fh:
        text = fh.read()

    lines = text.count("\n")
    if text and not text.endswith("\n"):
        lines += 1

    words = WORD_RE.findall(text.lower())
    counts = Counter(words)
    if counts:
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
