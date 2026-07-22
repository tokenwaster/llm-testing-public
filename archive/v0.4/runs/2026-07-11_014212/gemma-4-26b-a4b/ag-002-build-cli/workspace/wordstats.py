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
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Line count
    # splitlines() handles the trailing newline requirement correctly.
    # "a\n".splitlines() -> ['a'] (1 line)
    # "a\nb".splitlines() -> ['a', 'b'] (2 lines)
    # "".splitlines() -> [] (0 lines)
    # "\n".splitlines() -> [''] (1 line - an empty line)
    lines = content.splitlines()
    num_lines = len(lines)

    # Word extraction
    # A word is a maximal run of ASCII letters after lowercasing the whole text.
    words = re.findall(r'[a-z]+', content.lower())
    num_words = len(words)

    if num_words == 0:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Find the maximum frequency
        max_freq = max(counts.values())
        # Get all words with that frequency
        candidates = [word for word, count in counts.items() if count == max_freq]
        # Tie-breaker: alphabetical (earliest wins)
        top_word = min(candidates)
        top_count = max_freq

    print(f"lines: {num_lines}")
    print(f"words: {num_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
