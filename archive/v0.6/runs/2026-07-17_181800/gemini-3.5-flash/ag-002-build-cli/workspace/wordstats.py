import sys
import re
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
        
    filepath = sys.argv[1]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Count lines
    if not content:
        lines = 0
    else:
        content_for_lines = content[:-1] if content.endswith('\n') else content
        lines = content_for_lines.count('\n') + 1
        
    # Find words
    # A word is a maximal run of ASCII letters (a–z) after lowercasing the whole text.
    words = re.findall(r'[a-z]+', content.lower())
    total_words = len(words)
    
    # Count frequencies
    counts = Counter(words)
    if not counts:
        top_word, top_count = "-", 0
    else:
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))
        
    print(f"lines: {lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {top_count}")

if __name__ == '__main__':
    main()
