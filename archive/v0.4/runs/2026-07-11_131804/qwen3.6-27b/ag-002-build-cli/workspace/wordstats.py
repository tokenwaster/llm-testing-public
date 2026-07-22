import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, "r") as f:
        text = f.read()

    # Count lines: split by newline, but a trailing newline doesn't add an extra line
    # If text ends with \n, the last element after split is empty string, so we subtract 1
    # If text is empty, there are 0 lines
    if text == "":
        num_lines = 0
    else:
        lines = text.split("\n")
        # If the text ends with a newline, the last element is an empty string
        # which shouldn't count as a line
        if text.endswith("\n"):
            num_lines = len(lines) - 1
        else:
            num_lines = len(lines)

    # Extract words: maximal runs of ASCII letters after lowercasing
    lower_text = text.lower()
    words = re.findall(r"[a-z]+", lower_text)

    total_words = len(words)

    if total_words == 0:
        print(f"lines: {num_lines}")
        print(f"words: 0")
        print("top: - 0")
    else:
        word_counts = Counter(words)
        # Find the most frequent word; ties broken alphabetically (earliest wins)
        max_count = max(word_counts.values())
        # Get all words with max_count, sort alphabetically, pick first
        top_word = sorted(w for w, c in word_counts.items() if c == max_count)[0]
        print(f"lines: {num_lines}")
        print(f"words: {total_words}")
        print(f"top: {top_word} {max_count}")


if __name__ == "__main__":
    main()
