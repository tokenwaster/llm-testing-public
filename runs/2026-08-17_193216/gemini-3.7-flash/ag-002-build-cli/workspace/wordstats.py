import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = len(text.splitlines())
    words = re.findall(r'[a-z]+', text.lower())
    total_words = len(words)

    if total_words == 0:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Sort by (-count, word)
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))

    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
