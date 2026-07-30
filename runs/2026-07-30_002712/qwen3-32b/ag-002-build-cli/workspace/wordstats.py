import sys
import re
from collections import Counter

def main():
    path = sys.argv[1]
    with open(path, 'r') as f:
        text = f.read()
    num_lines = len(text.splitlines())
    words = re.findall(r'[a-z]+', text.lower())
    total_words = len(words)
    
    if not words:
        top_word = '-'
        count = 0
    else:
        counter = Counter(words)
        sorted_items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
        top_word, count = sorted_items[0]
    
    print(f"lines: {num_lines}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {count}")

if __name__ == '__main__':
    main()