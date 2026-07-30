#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-text-file>", file=sys.stderr)
        return 1
    
    filepath = sys.argv[1]
    
    # Read the entire text file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        return 1
    
    # Count lines (split by newline; trailing final newline does not add an extra line)
    if content == "":
        num_lines = 0
    else:
        # Split on newlines, but handle the case properly
        lines = content.split('\n')
        # If file ends with a newline, last element will be empty string - remove it
        if lines and lines[-1] == '':
            lines.pop()
        num_lines = len(lines)
    
    # Extract words: maximal runs of ASCII letters (a-z) after lowercasing
    content_lower = content.lower()
    current_word = []
    words = []
    
    for ch in content_lower:
        if 'a' <= ch <= 'z':
            current_word.append(ch)
        else:
            if current_word:
                words.append(''.join(current_word))
                current_word = []
    
    # Don't forget the last word if file doesn't end with a separator
    if current_word:
        words.append(''.join(current_word))
    
    # Count frequencies and find top word
    if not words:
        print(f"lines: {num_lines}")
        print(f"words: 0")
        print("top: - 0")
    else:
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        
        # Find max count
        max_count = max(freq.values())
        
        # Get all words with that count and sort alphabetically
        top_words_with_max = [word for word, count in freq.items() if count == max_count]
        top_word = min(top_words_with_max)  # earliest alphabetically
        
        print(f"lines: {num_lines}")
        print(f"words: {len(words)}")
        print(f"top: {top_word} {max_count}")

if __name__ == "__main__":
    main()
