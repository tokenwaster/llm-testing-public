import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Calculate lines
    # A trailing final newline does not add an extra line.
    if not content:
        lines_count = 0
    else:
        lines = content.split('\n')
        if len(lines) > 1 and lines[-1] == '':
            lines_count = len(lines) - 1
        else:
            lines_count = len(lines)
            
    # A word is a maximal run of ASCII letters (a-z) after lowercasing the whole text.
    # Digits, punctuation and underscores separate words.
    content_lower = content.lower()
    words = re.findall(r'[a-z]+', content_lower)
    
    total_words = len(words)
    
    if total_words == 0:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        # Ties are broken alphabetically (earliest wins).
        sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, top_count = sorted_counts[0]
        
    print(f"lines: {lines_count}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
