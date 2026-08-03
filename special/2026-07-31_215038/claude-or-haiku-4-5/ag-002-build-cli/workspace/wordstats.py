import sys
import re

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if content == "":
        num_lines = 0
    else:
        num_lines = len(content.rstrip('\n').split('\n')) if content.rstrip('\n') else 0
    
    text_lower = content.lower()
    
    words = re.findall(r'[a-z]+', text_lower)
    
    word_count = len(words)
    
    if word_count == 0:
        top_word = "-"
        top_count = 0
    else:
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        max_count = max(word_freq.values())
        candidates = [word for word, count in word_freq.items() if count == max_count]
        top_word = min(candidates)
        top_count = max_count
    
    print(f"lines: {num_lines}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    main()
