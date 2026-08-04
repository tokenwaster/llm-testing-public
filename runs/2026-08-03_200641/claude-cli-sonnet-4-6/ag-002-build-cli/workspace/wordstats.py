import sys
import re
from collections import Counter

def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    line_count = len(lines)

    words = re.findall(r"[a-z]+", text.lower())
    word_count = len(words)

    if not words:
        print(f"lines: {line_count}")
        print(f"words: {word_count}")
        print("top: - 0")
        return

    counts = Counter(words)
    top_word = min(counts, key=lambda w: (-counts[w], w))
    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {counts[top_word]}")

if __name__ == "__main__":
    main()
