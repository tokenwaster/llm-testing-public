import re
import sys
from collections import Counter

def main():
    path = sys.argv[1]
    text = open(path, encoding="utf-8").read()

    lines = text.splitlines()
    line_count = len(lines)

    words = re.findall(r'[a-z]+', text.lower())
    word_count = len(words)

    if words:
        counts = Counter(words)
        top_word, top_count = min(
            ((w, c) for w, c in counts.items() if c == max(counts.values())),
            key=lambda x: x[0]
        )
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
