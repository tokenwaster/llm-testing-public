import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        return
    
    filepath = sys.argv[1]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count lines using splitlines (handles trailing newline correctly)
    lines = len(content.splitlines())
    
    # Convert to lowercase and extract words (maximal runs of ASCII letters a-z)
    content_lower = content.lower()
    words = re.findall(r'[a-z]+', content_lower)
    
    total_words = len(words)
    
    if total_words == 0:
        top_word = '-'
        top_count = 0
    else:
        word_counts = Counter(words)
        max_count = max(word_counts.values())
        candidates = [word for word, count in word_counts.items() if count == max_count]
        # Alphabetical tie-breaker: earliest wins
        top_word = min(candidates)
        top_count = max_count
    
    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
