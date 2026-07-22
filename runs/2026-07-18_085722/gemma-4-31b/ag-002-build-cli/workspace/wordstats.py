import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)

    # Line count
    # splitlines() handles trailing newlines correctly according to the requirement
    # "a\nb\n".splitlines() -> ['a', 'b'] (length 2)
    # "".splitlines() -> [] (length 0)
    lines = len(content.splitlines())

    # Word extraction: maximal run of ASCII letters [a-z] after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    if not words:
        top_word, top_freq = "-", 0
    else:
        counts = Counter(words)
        # Sort by frequency descending (-x[1]), then alphabetically ascending (x[0])
        sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_freq = sorted_words[0]

    print(f"lines: {lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_freq}")

if __name__ == "__main__":
    main()
