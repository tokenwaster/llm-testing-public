import sys
import re

def main():
    file_path = sys.argv[1]
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    line_count = len(lines)
    
    words = []
    for line in lines:
        lower_line = line.lower()
        words_in_line = re.findall(r'[a-z]+', lower_line)
        words.extend(words_in_line)
    
    word_count = len(words)
    
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    
    if not words:
        top_word = '-'
        max_count = 0
    else:
        # Find the maximum count
        max_count = max(counts.values())
        candidates = [word for word, cnt in counts.items() if cnt == max_count]
        # Sort lex order to break ties
        candidates.sort()
        top_word = candidates[0]
    
    print(f"lines: {line_count}")
    print(f"words: {word_count}")
    print(f"top: {top_word} {max_count}")

if __name__ == '__main__':
    main()