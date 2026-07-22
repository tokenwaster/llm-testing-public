import sys
import re
from collections import Counter

def analyze_file(filepath):
    """Reads the file and calculates line count, total words, and top word."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: File not found.", file=sys.stderr)
        return None

    # 1. Calculate lines: splitlines() handles various newline types and correctly counts lines.
    lines = len(content.splitlines())

    # 2. Extract words: maximal run of ASCII letters (a-z) after lowercasing.
    words = re.findall(r'[a-z]+', content.lower())

    total_word_count = len(words)

    # 3. Find top word
    if not words:
        return lines, total_word_count, "- ", 0
    else:
        counts = Counter(words)
        
        # Sorting criteria: Highest count first (descending), then alphabetically earliest word (ascending).
        # We use a custom sort key: (-count, word).
        # -count ensures that the highest count comes first when sorting ascendingly.
        # word ensures that ties in count are broken by alphabetical order.
        sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        
        best_word, top_count = sorted_items[0]

    return lines, total_word_count, best_word, top_count

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    result = analyze_file(filepath)

    if result is None:
        sys.exit(1)

    lines, total_word_count, best_word, top_count = result

    print(f"lines: {lines}")
    print(f"words: {total_word_count}")
    print(f"top: {best_word} {top_count}")


if __name__ == "__main__":
    main()