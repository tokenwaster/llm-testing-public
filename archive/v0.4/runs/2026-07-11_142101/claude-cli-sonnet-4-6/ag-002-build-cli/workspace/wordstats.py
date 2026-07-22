import sys
import re
from collections import Counter

def main():
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    line_count = len(lines)

    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    if words:
        counts = Counter(words)
        top_word = min(counts, key=lambda w: (-counts[w], w))
        top_count = counts[top_word]
        top_str = f"{top_word} {top_count}"
    else:
        top_str = "- 0"

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_str}")

if __name__ == '__main__':
    main()
