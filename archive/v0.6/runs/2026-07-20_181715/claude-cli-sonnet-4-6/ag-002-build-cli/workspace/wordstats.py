import re
import sys
from collections import Counter

def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    words = re.findall(r'[a-z]+', text.lower())

    counts = Counter(words)
    if counts:
        top_word = min(counts, key=lambda w: (-counts[w], w))
        top_count = counts[top_word]
        top_str = f"{top_word} {top_count}"
    else:
        top_str = "- 0"

    print(f"lines: {len(lines)}")
    print(f"words: {len(words)}")
    print(f"top: {top_str}")

if __name__ == "__main__":
    main()
