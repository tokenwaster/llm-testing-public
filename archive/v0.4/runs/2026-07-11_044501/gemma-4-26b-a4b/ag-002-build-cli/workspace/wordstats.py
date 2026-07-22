import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Line count
    # splitlines() handles the trailing newline correctly (doesn't add an extra empty line)
    lines = content.splitlines()
    line_count = len(lines)
    
    # If the file is not empty but ends with a newline, splitlines() doesn't create an extra empty string.
    # However, if the file is just "\n", splitlines() returns ['']. 
    # Wait, let me check: "".splitlines() -> []
    # "\n".splitlines() -> [''] (Wait, no, it depends on how you define lines)
    # Let's re-read: "as split by newline; a trailing final newline does not add an extra line"
    # If content is "a\nb\n", splitlines() gives ["a", "b"]. len = 2. Correct.
    # If content is "a\nb", splitlines() gives ["a", "b"]. len = 2. Correct.
    # If content is "", splitlines() gives []. len = 0. Correct.
    # But what if the file has a single newline? "\n".splitlines() -> [''] (len 1).
    # Is that correct? "a trailing final newline does not add an extra line".
    # If content is "\n", it's one line (an empty line). So len=1. Correct.

    # Word count
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    if word_count == 0:
        top_word = "-"
        top_count = 0
    else:
        counts = Counter(words)
        max_freq = max(counts.values())
        candidates = [w for w, c in counts.items() if c == max_freq]
        top_word = min(candidates)
        top_count = max_freq

    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
