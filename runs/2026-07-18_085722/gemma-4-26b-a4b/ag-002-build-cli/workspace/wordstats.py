import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Line count
    # splitlines() handles the trailing newline requirement correctly.
    # "" -> [] (0 lines)
    # "a\n" -> ["a"] (1 line)
    # "a\nb" -> ["a", "b"] (2 lines)
    lines = content.splitlines()
    num_lines = len(lines)

    # Word extraction
    # Lowercase the whole text first
    lower_content = content.lower()
    # Find all maximal runs of ASCII letters [a-z]
    words = re.findall(r'[a-z]+', lower_content)
    num_words = len(words)

    if num_words == 0:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Sort by count (descending) and then word (ascending)
        # We can use sorted() with a custom key.
        # To sort by count descending, we use -x[1].
        # To sort by word ascending, we use x[0].
        sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_counts[0]

    print(f"lines: {num_lines}")
    print(f"words: {num_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
