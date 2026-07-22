import sys
import re
from collections import Counter

def analyze_wordstats(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: File not found.", file=sys.stderr)
        return

    # 1. Calculate lines
    # splitlines() handles various newline conventions and correctly counts lines
    # without adding an extra line for a trailing newline.
    line_count = len(content.splitlines())

    # 2. Process words
    # Lowercase the whole text first.
    lower_text = content.lower()
    
    # A word is a maximal run of ASCII letters (a-z).
    # We use regex to find all such runs.
    words = re.findall(r'[a-z]+', lower_text)

    # 3. Calculate total words and frequency map
    total_word_count = len(words)
    word_counts = Counter(words)

    # 4. Determine top word
    if not word_counts:
        top_word = "-"
        top_count = 0
    else:
        max_count = max(word_counts.values())
        
        # Find all words that match the max count (potential ties)
        candidates = [word for word, count in word_counts.items() if count == max_count]
        
        # Tie-breaker: alphabetically earliest wins. Sort and take the first one.
        top_word = sorted(candidates)[0]
        top_count = max_count

    # 5. Print results
    print(f"lines: {line_count}")
    print(f"words: {total_word_count}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        # For testing purposes, we might want to handle no arguments gracefully, 
        # but based on usage, we expect exactly one argument (the file path).
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyze_wordstats(file_path)