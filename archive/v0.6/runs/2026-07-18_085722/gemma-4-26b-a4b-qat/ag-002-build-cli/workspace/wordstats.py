import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Count lines
    # "as split by newline; a trailing final newline does not add an extra line"
    # splitlines() handles this correctly.
    if not content:
        lines_count = 0
    else:
        lines_count = len(content.splitlines())

    # Find words: maximal run of ASCII letters (a-z) after lowercasing
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    if word_count == 0:
        print(f"lines: {lines_count}")
        print(f"words: 0")
        print(f"top: - 0")
        return

    counts = Counter(words)
    
    # Find the most frequent word. 
    # Ties are broken alphabetically (earliest wins).
    # We want max count, then min word.
    # We can sort by (-count, word)
    sorted_counts = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    top_word, top_count = sorted_counts[0]

    print(f"lines: {lines_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
