import sys
import re
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Count lines: split by newline, but a trailing newline does not add an extra line
    if text.endswith("\n"):
        text_no_trailing = text[:-1]
    else:
        text_no_trailing = text

    if text_no_trailing == "":
        num_lines = 0
    else:
        num_lines = text_no_trailing.count("\n") + 1

    # Lowercase the whole text, then find all maximal runs of ASCII letters
    lower_text = text.lower()
    words = re.findall(r"[a-z]+", lower_text)

    total_words = len(words)

    if total_words == 0:
        top_word = "-"
        top_count = 0
    else:
        word_counts = Counter(words)
        # Sort by (-count, word) to get most frequent first, ties broken alphabetically
        top_word, top_count = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))[0]

    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
