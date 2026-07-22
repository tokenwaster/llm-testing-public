import sys
import re
from collections import Counter

def analyze_wordstats(filepath):
    """
    Analyzes a text file to count lines, total words, and find the most frequent word.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: File not found.", file=sys.stderr)
        return None

    # 1. Count lines
    # splitlines() correctly handles the definition where a trailing newline doesn't add an extra line.
    lines_count = len(content.splitlines())

    # 2. Extract and count words
    # A word is a maximal run of ASCII letters after lowercasing.
    text_lower = content.lower()
    words = re.findall(r'[a-z]+', text_lower)
    word_count = len(words)

    if not words:
        top_word = "- "
        top_count = 0
    else:
        # Count frequencies
        counts = Counter(words)
        
        # Find the top word. Tie-breaking rule: alphabetically earliest wins.
        # We sort by count (descending), then by word (ascending).
        # max() with a key is usually better for this, but since we need specific tie-breaking 
        # (alphabetical order *wins* ties in frequency), sorting the items explicitly is safer.
        
        # Get unique words and sort them alphabetically first to ensure consistent tie-breaking check
        unique_words = sorted(counts.keys())
        
        best_word = ""
        max_count = -1

        for word in unique_words:
            current_count = counts[word]
            if current_count > max_count:
                max_count = current_count
                best_word = word
            # Because we iterate over sorted keys, if a tie occurs (current_count == max_count), 
            # the 'best_word' remains unchanged, satisfying the "alphabetically earliest wins" rule.

        top_word = best_word
        top_count = max_count


    # Print results in the required format
    print(f"lines: {lines_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        # If run without arguments, print usage help (optional but good practice)
        sys.exit(1)
    
    filepath = sys.argv[1]
    analyze_wordstats(filepath)