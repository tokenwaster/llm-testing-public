import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        sys.exit(1)

    # Line count
    # splitlines() handles trailing newlines correctly according to the prompt
    lines_count = len(content.splitlines())

    # Word processing
    text_lower = content.lower()
    words = re.findall(r'[a-z]+', text_lower)
    total_words = len(words)

    if not words:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Sort by count descending, then word ascending
        # -x[1] for count desc, x[0] for alphabetical asc
        sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_words[0]

    print(f"lines: {lines_count}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
