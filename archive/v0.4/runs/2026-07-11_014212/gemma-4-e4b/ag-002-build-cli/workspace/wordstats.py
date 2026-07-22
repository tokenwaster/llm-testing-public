import sys
import re
from collections import Counter

def analyze_text(filepath):
    """
    Analyzes a text file to count lines, words, and find the top word.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: File not found.", file=sys.stderr)
        return None

    # 1. Calculate lines
    # The number of lines is the count of newline characters, unless the file is empty.
    # If content is non-empty, it's generally len(content.splitlines())
    if not content:
        line_count = 0
    else:
        # splitlines() handles various line endings and correctly counts lines
        line_count = content.count('\\n') + (1 if content.endswith('\\n') else 0)
        # A simpler way that matches the requirement ("as split by newline; a trailing final newline does not add an extra line") is usually just counting actual newlines, but let's stick to standard Python file reading behavior for robustness.
        # If we read it and count lines:
        line_count = content.count('\\n') + 1 if content else 0 # This is tricky due to how splitlines works vs raw newline counts. Let's use the reliable method of counting actual newlines, but adjusting for the trailing newline rule.

        # Re-evaluating line count:
        # If we read "a\nb", lines = 2. content.count('\n') = 1.
        # If we read "a\nb\n", lines = 2. content.count('\n') = 2. (Wait, the requirement says trailing newline does not add an extra line).
        # Example: 'hello\nworld' -> 2 lines. count('\n')=1.
        # Example: 'hello\nworld\n' -> 2 lines. count('\n')=2. This is where the ambiguity lies.

        # Standard Python approach for counting lines based on splitlines():
        line_count = len(content.splitlines())


    # 2. Calculate words and word counts
    # A word is a maximal run of ASCII letters (a-z) after lowercasing.
    # We use regex to find all sequences of one or more ASCII letters.
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    # 3. Find the top word
    if not words:
        top_word = "- "
        top_count = 0
    else:
        counts = Counter(words)
        # Get items sorted by count (descending), then by word (ascending for tie-breaking).
        # The key function returns a tuple (-count, word). We negate the count because Python's sort is ascending.
        # Sorting by (-count, word) ensures:
        # 1. Highest count comes first (due to negative sign).
        # 2. For equal counts, lexicographically smallest word comes first.
        sorted_words = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        top_word, top_count = sorted_words[0]

    # Print the required output format
    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        # If no argument is provided, print usage and exit gracefully (or handle as per requirement).
        # For testing purposes, we assume the script will be called correctly.
        pass
    else:
        filepath = sys.argv[1]
        analyze_text(filepath)