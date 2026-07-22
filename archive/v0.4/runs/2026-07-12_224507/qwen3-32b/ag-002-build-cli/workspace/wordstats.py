import sys
import re
from collections import Counter

def main():
    input_path = sys.argv[1]
    with open(input_path, 'r') as f:
        content = f.read()

    lines = len(content.splitlines())
    words = re.findall(r'[a-z]+', content.lower())
    word_count = len(words)

    if not words:
        top_line = 'top: - 0'
    else:
        counts = Counter(words)
        max_freq = max(counts.values())
        candidates = [word for word, cnt in counts.items() if cnt == max_freq]
        top_word = min(candidates)
        top_line = f'top: {top_word} {max_freq}'

    print(f'lines: {lines}')
    print(f'words: {word_count}')
    print(top_line)

if __name__ == '__main__':
    main()