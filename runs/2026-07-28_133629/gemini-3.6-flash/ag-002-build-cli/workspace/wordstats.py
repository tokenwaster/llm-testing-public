import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    filepath = sys.argv[1]
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    lines = len(content.splitlines())
    words = re.findall(r'[a-z]+', content.lower())
    total_words = len(words)

    if total_words == 0:
        top_str = "- 0"
    else:
        counts = Counter(words)
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))
        top_str = f"{top_word} {top_count}"

    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_str}")

if __name__ == '__main__':
    main()
