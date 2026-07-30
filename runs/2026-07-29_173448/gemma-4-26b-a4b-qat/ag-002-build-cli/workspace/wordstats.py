import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Count lines
    # "a trailing final newline does not add an extra line"
    # content.splitlines() handles this well.
    # However, splitlines() might not work exactly if the last line is empty.
    # Let's check requirements. 
    # "lines is the number of lines in the file (as split by newline; a trailing final newline does not add an extra line)."
    # This usually means if the file ends in \n, it's not a new empty line.
    # Example: "a\nb\n" -> lines: 2.
    # Example: "a\nb" -> lines: 2.
    # Example: "" -> lines: 0.
    
    if not content:
        lines_count = 0
    else:
        # splitlines() handles trailing newline correctly for counting
        lines_count = len(content.splitlines())
        # Actually, if content is "a\n", splitlines() gives ['a'], len=1. Correct.
        # If content is "a\n\n", splitlines() gives ['a', ''], len=2. Correct.
        # If content is "a", splitlines() gives ['a'], len=1. Correct.
        # If content is "", splitlines() gives [], len=0. Correct.
        # Wait, let's re-read: "a trailing final newline does not add an extra line"
        # If file is "a\n", lines=1.
        # If file is "a\nb", lines=2.
        # If file is "a\nb\n", lines=2.
        # This is exactly what splitlines() does.

    # Count words
    # A word is a maximal run of ASCII letters (a-z) after lowercasing.
    # Digits, punctuation and underscores separate words.
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    # Top word
    if word_count == 0:
        top_line = "top: - 0"
    else:
        counts = Counter(words)
        # Tie-breaking: most frequent, then earliest alphabetically.
        # We can sort by (-count, word)
        # items() returns (word, count)
        # Sort by -count (descending) and word (ascending)
        sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_counts[0]
        top_line = f"top: {top_word} {top_count}"

    print(f"lines: {lines_count}")
    print(f"words: {word_count}")
    print(top_line)

if __name__ == "__main__":
    main()
