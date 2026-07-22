import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    path = sys.argv[1]

    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Count lines: split by newline, ignore trailing empty from final newline
    if text == '':
        lines = 0
    else:
        parts = text.split('\n')
        if parts[-1] == '':
            parts.pop()
        lines = len(parts)

    # Words: lowercase, then find runs of ASCII letters
    lower_text = text.lower()
    words = re.findall(r'[a-z]+', lower_text)
    word_count = len(words)

    # Most frequent word
    if word_count == 0:
        top_word = '-'
        top_count = 0
    else:
        counter = Counter(words)
        # Sort by count descending, then alphabetically ascending
        top_word, top_count = min(counter.items(), key=lambda x: (-x[1], x[0]))

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()