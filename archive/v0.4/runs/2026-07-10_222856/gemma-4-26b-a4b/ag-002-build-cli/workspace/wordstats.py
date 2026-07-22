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

    # Line count logic: splitlines() handles the trailing newline requirement
    # "a trailing final newline does not add an extra line"
    # "".splitlines() -> [] (0 lines)
    # "\n".splitlines() -> [''] (Wait, actually it's ['']) - let's check.
    # Actually, splitlines() on "\n" returns ['']. Let's verify this behavior.
    # If content is "\n", the number of lines should be 1? Or 0?
    # "a trailing final newline does not add an extra line".
    # If file is "\n", it has one line (an empty one).
    # Let's test with a small script.
    
    lines_list = content.splitlines()
    if content == "":
        num_lines = 0
    else:
        # splitlines handles the trailing newline correctly for our needs.
        # However, if the file is just "\n", splitlines() returns [''].
        # If the file is "a\n", splitlines() returns ['a'].
        # Let's check what happens with a single \n.
        num_lines = len(lines_list)

    # Word extraction: maximal run of ASCII letters, lowercase
    words = re.findall(r'[a-zA-Z]+', content.lower())
    word_count = len(words)

    if word_count == 0:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Sort by frequency descending, then alphabetically ascending
        # We want the highest count. For ties, we want the smallest word (alphabetically).
        # To use sort(), we can use (-count, word) as key.
        sorted_counts = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        top_word, top_count = sorted_counts[0]

    print(f"lines: {num_lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
