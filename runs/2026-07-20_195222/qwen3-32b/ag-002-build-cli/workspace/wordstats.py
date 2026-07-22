import sys
import re
from collections import defaultdict

def main():
    input_path = sys.argv[1]
    with open(input_path, 'r') as f:
        content = f.read()

    lines = len(content.splitlines())
    words_matches = re.findall(r'[A-Za-z]+', content)
    words = [w.lower() for w in words_matches]
    word_count = len(words)

    counts = defaultdict(int)
    for word in words:
        counts[word] += 1

    if not words:
        print(f"lines: {lines}")
        print(f"words: 0")
        print("top: - 0")
    else:
        sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_counts[0]
        print(f"lines: {lines}")
        print(f"words: {word_count}")
        print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()