import re
import sys


def main():
    if len(sys.argv) != 2:
        print("usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if text == "":
        lines = 0
    else:
        stripped = text[:-1] if text.endswith("\n") else text
        lines = stripped.count("\n") + 1

    words = re.findall(r"[a-z]+", text.lower())

    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1

    if counts:
        top_word, top_count = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {lines}")
    print(f"words: {len(words)}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
