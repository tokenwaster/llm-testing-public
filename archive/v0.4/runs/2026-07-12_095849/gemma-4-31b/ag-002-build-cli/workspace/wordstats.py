import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        return

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return

    # Line count: a trailing final newline does not add an extra line.
    # splitlines() handles this correctly.
    lines_count = len(content.splitlines()) if content else 0
    # Special case for empty file vs file with only newlines
    if not content:
        lines_count = 0
    elif content == '\n' * len(content):
        # If the file consists only of newlines, splitlines() might return an empty list or a list of empty strings.
        # Let's re-evaluate based on "split by newline; trailing final newline does not add extra line".
        # Example: "\n" -> 1 line? Or 0 lines? Usually "\n" is one empty line followed by EOF.
        # Actually, if the file is just "\n", splitlines() returns ['']. len is 1.
        # If the file is "a\n", splitlines() returns ['a']. len is 1.
        # This seems to match the requirement.
        pass

    # Words: maximal run of ASCII letters (a-z) after lowercasing.
    words = re.findall(r'[a-z]+', content.lower())
    total_words = len(words)
    
    if not words:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Sort by count descending, then word ascending
        # sorted returns a list of tuples (word, count)
        sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_words[0]

    print(f"lines: {lines_count}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
