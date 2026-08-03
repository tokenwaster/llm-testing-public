import sys
import re
from collections import Counter

def wordstats(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    lines = len(content.splitlines())

    text_lower = content.lower()
    words = re.findall(r'[a-z]+', text_lower)
    word_count = len(words)

    if words:
        word_freq = Counter(words)
        top_word, top_count = min(word_freq.items(), key=lambda x: (-x[1], x[0]))
    else:
        top_word, top_count = '-', 0

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
    wordstats(sys.argv[1])
