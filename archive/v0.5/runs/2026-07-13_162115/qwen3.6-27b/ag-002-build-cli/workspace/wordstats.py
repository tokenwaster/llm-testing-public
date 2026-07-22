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
    # If the file ends with \n, the last element after split will be empty string
    # We need to count lines as the number of newline-separated segments
    if text == "":
        num_lines = 0
    else:
        # Split by newline; if text ends with \n, the last element is ''
        # We want to count that as not an extra line
        lines = text.split("\n")
        if text.endswith("\n"):
            num_lines = len(lines) - 1
        else:
            num_lines = len(lines)

    # Extract words: maximal runs of ASCII letters after lowercasing
    lower_text = text.lower()
    words = re.findall(r"[a-z]+", lower_text)

    word_count = len(words)

    if word_count == 0:
        print(f"lines: {num_lines}")
        print(f"words: 0")
        print("top: - 0")
    else:
        counter = Counter(words)
        # Find max count
        max_count = max(counter.values())
        # Get all words with max count, sort alphabetically, pick first
        top_candidates = [w for w, c in counter.items() if c == max_count]
        top_candidates.sort()
        top_word = top_candidates[0]

        print(f"lines: {num_lines}")
        print(f"words: {word_count}")
        print(f"top: {top_word} {max_count}")


if __name__ == "__main__":
    main()
