import sys
import re
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    lines = content.splitlines()
    line_count = len(lines) if lines or content == "" else 0
    if content == "":
        line_count = 0
    else:
        line_count = len(content.splitlines())
    
    content_lower = content.lower()
    words = re.findall(r'[a-z]+', content_lower)
    
    word_count = len(words)
    
    if word_count == 0:
        top_word = "-"
        top_count = 0
    else:
        word_counter = Counter(words)
        top_word, top_count = sorted(word_counter.items(), key=lambda x: (-x[1], x[0]))[0]
    
    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
