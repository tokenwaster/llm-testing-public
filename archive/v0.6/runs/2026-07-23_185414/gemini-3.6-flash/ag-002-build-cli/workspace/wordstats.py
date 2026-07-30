import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
        
    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    lines_count = len(text.splitlines())
    words = re.findall(r'[a-z]+', text.lower())
    words_count = len(words)

    if words:
        counts = Counter(words)
        top_word, top_count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    else:
        top_word, top_count = '-', 0

    print(f"lines: {lines_count}")
    print(f"words: {words_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
