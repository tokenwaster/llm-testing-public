import re
import sys


def main():
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    if text.endswith("\n"):
        line_count = text.count("\n")
    else:
        line_count = text.count("\n") + 1 if text else 0

    words = re.findall(r"[a-z]+", text.lower())

    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1

    if counts:
        top_word = min(counts, key=lambda w: (-counts[w], w))
        top_count = counts[top_word]
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
