import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Line count
    # splitlines() handles the trailing newline correctly according to requirements.
    # If content is empty, lines should be 0.
    if not content:
        line_count = 0
    else:
        # We need to be careful with how splitlines works for a single \n.
        # "a\n".splitlines() -> ['a'] (1 line)
        # "\n".split    lines() -> [''] (1 line? No, let's check)
        # Actually, the requirement says: "as split by newline; a trailing final newline does not add an extra line"
        # Let's use a more manual approach to be sure.
        line_count = content.split('\n').count('') # This is wrong.
        # Let's re-read: "lines is the number of lines in the file (as split by newline; a trailing final newline does not add an extra line)"
        # If content is "a\nb\n", it should be 2 lines.
        # If content is "a\nb", it should be 2 lines.
        # If content is "", it should be 0 lines.
        # If content is "\n", it should be 1 line (the first line is empty).
        
        # Let's use split('\n') and handle the trailing newline.
        lines = content.split('\n')
        if len(lines) > 1 and lines[-1] == '':
            line_count = len(lines) - 1
        else:
            line_count = len(lines)
            
        # Wait, if content is "", split('\n') gives ['']. That's 1 line. But it should be 0.
        if not content:
            line_count = 0
    
    # Re-evaluating line count logic:
    # "a\nb" -> ["a", "b"] -> 2 lines
    # "a\nb\n" -> ["a", "b", ""] -> 2 lines (because trailing newline doesn't add extra)
    # "" -> []? No, "".split('\n') is ['']
    
    # Let's try this:
    if not content:
        line_count = 0
    else:
        lines_list = content.split('\n')
        if lines_list[-1] == '':
            line_count = len(lines_list) - 1
        else:
            line_count = len(lines_list)

    # Word count and top word
    # A word is a maximal run of ASCII letters (a-z) after lowercasing.
    words = re.findall(r'[a-z]+', content.lower())
    word_counts = Counter(words)
    total_words = len(words)

    if not words:
        top_word = "-"
        top_count = 0
    else:
        # Sort by frequency (descending) and then alphabetically (ascending).
        # We can use a custom key for sorting.
        # To sort by (-count, word), we can do:
        sorted_words = sorted(word_counts.items(), key=lambda item: (-item[1], item[0]))
        top_word, top_count = sorted_words[0]

    print(f"lines: {line_count}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
