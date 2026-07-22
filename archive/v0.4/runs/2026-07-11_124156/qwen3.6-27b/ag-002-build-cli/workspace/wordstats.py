import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, "r") as f:
        content = f.read()

    # Count lines: split by newline, but a trailing newline doesn't add an extra line
    # If content ends with '\n', the last split element is empty and should not count
    lines = content.split("\n")
    if content.endswith("\n") and len(lines) > 0:
        line_count = len(lines) - 1
    else:
        line_count = len(lines)

    # Extract words: maximal runs of ASCII letters after lowercasing
    lowercased = content.lower()
    words = re.findall(r"[a-z]+", lowercased)

    word_count = len(words)

    if word_count == 0:
        print(f"lines: {line_count}")
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

        print(f"lines: {line_count}")
        print(f"words: {word_count}")
        print(f"top: {top_word} {max_count}")


if __name__ == "__main__":
    main()
