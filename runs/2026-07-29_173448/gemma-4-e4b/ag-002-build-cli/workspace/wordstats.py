import sys
import re
from collections import Counter

def get_word_stats(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: File not found.")
        sys.exit(1)

    # 1. Line Count Calculation
    # Using splitlines() is generally the most robust way to count lines,
    # as it handles different newline conventions and avoids double counting due to trailing newlines.
    lines = content.splitlines()
    line_count = len(lines)

    # 2. Word Extraction and Total Count
    lower_text = content.lower()
    # A word is a maximal run of ASCII letters (a-z).
    words = re.findall(r'[a-z]+', lower_text)
    total_word_count = len(words)

    # 3. Top Word Calculation
    if not words:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        max_count = max(counts.values())

        # Find all words that match the maximum count
        most_frequent_candidates = [word for word, count in counts.items() if count == max_count]

        # Tiebreaker rule: Ties are broken alphabetically (earliest wins).
        # This means we select the minimum word among the candidates.
        top_word = min(most_frequent_candidates)
        top_count = max_count

    # 4. Print Output
    print(f"lines: {line_count}")
    print(f"words: {total_word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        # This shouldn't happen if the harness calls it correctly, but good practice for a CLI tool.
        # print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    get_word_stats(filepath)