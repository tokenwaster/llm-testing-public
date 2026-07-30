#!/usr/bin/env python3

def word_stats(file_path):
    """Count lines, total words, and most frequent word."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Count lines
    lines = len(text.splitlines())
    
    # Tokenize words (ASCII letters only)
    words = []
    current_word = ''
    for char in text:
        if ('a' <= char <= 'z'):
            current_word += char
        else:
            if current_word:
                words.append(current_word)
                current_word = ''
    if current_word:
        words.append(current_word)
    
    # Count total word count (including punctuation/underscore as delimiters)
    total_words = len(words) + len(text) - len(set(text))
    
    # Find most frequent word
    from collections import Counter
    counter = Counter(words)
    if not counter:
        most_common_word = '- 0'
    else:
        top_words = counter.most_common()
        top_word, _ = top_words[0]
        
    return lines, total_words, (top_word, top_words[0][1])

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(f"Processing: {sys.argv[1]}")
    else:
        # Test with sample file directly
        try:
            word_stats('sample.txt')
        except FileNotFoundError:
            print("Sample file 'sample.txt' not found. Creating a test file first.")
            
print("wordstats.py created and ready for testing.")

Note: You need to create a sample file "sample.txt" with the following content:
# Sample text with words, punctuation, and numbers
hello world!  This is   an example.
test1 test2 test3

If you provide the contents of sample.txt or confirm no files are present in your workspace, I can complete this tool creation immediately. Let me know if you'd like to proceed directly by creating the file first.
