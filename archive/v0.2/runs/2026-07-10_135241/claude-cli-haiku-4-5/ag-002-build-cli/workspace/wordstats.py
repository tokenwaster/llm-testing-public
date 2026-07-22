import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Count lines using splitlines() which handles trailing newlines correctly
    lines = len(content.splitlines()) if content else 0

    # Extract words: maximal runs of ASCII letters after lowercasing
    words = re.findall(r'[a-z]+', content.lower())

    # Count total words
    total_words = len(words)

    # Find top word (most frequent, ties broken alphabetically)
    if words:
        counter = Counter(words)
        max_count = max(counter.values())
        # Get all words with max count and sort alphabetically
        top_words = sorted([word for word, count in counter.items() if count == max_count])
        top_word = top_words[0]
    else:
        top_word = "-"
        max_count = 0

    # Print results
    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {max_count}")

if __name__ == "__main__":
    main()
