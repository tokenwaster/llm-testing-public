import sys
import re
from collections import Counter

def analyze_text(filepath):
    """
    Analyzes a text file to count lines, words, and find the most frequent word.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: File not found.", file=sys.stderr)
        return None

    # 1. Calculate lines
    # The number of lines is typically len(content.splitlines())
    # If the file ends with a newline, splitlines() handles it correctly.
    # Example: "a\nb" -> ['a', 'b'] (2 lines). "a\n" -> ['a'] (1 line).
    lines = content.count('\\n') + 1 if content else 0
    if not content and filepath == "": # Handle empty file case explicitly
        lines = 0

    # A more robust way to count lines:
    # If the file is truly empty, it has 0 lines.
    # Otherwise, splitlines() gives the correct count unless the file was read as an empty string for some reason.
    if not content:
        lines = 0
    else:
        lines = len(content.splitlines())


    # 2. Extract and count words
    # A word is a maximal run of ASCII letters (a-z) after lowercasing.
    # We use regex to find all sequences of one or more letters [a-zA-Z].
    words = re.findall(r'[a-zA-Z]+', content, flags=re.IGNORECASE)
    word_count = len(words)

    if not words:
        return {
            "lines": lines,
            "words": word_count,
            "top": ("-", 0)
        }

    # Count frequencies
    word_counts = Counter(w.lower() for w in words)

    # Find the top word based on frequency and alphabetical tie-breaking
    # We need to sort by:
    # 1. Frequency (descending) -> -count
    # 2. Word (ascending/alphabetical) -> word
    # The max function with a custom key is usually better for this pattern,
    # but since we are looking for the *best* candidate among all keys, sorting and picking the first element is clearer.

    # Get items: [(word, count), ...]
    sorted_items = sorted(
        word_counts.items(), 
        key=lambda item: (-item[1], item[0]) # Sort by -count (desc) then word (asc)
    )

    top_word, top_count = sorted_items[0]

    return {
        "lines": lines,
        "words": word_count,
        "top": (top_word, top_count)
    }


def main():
    if len(sys.argv) != 2:
        # The prompt implies usage is handled by the caller/harness, but good practice dictates checking args.
        # Since this is a tool implementation, we assume correct calling context for now.
        pass

    filepath = sys.argv[1]
    stats = analyze_text(filepath)

    if stats:
        print(f"lines: {stats['lines']}")
        print(f"words: {stats['words']}")
        print(f"top: {stats['top'][0]} {stats['top'][1]}")


if __name__ == "__main__":
    main()