import sys
import re
from collections import Counter

def main():
    path = sys.argv[1]
    with open(path, 'r') as f:
        content = f.read()

    line_count = len(content.splitlines())
    words_list = re.findall(r'[a-zA-Z]+', content.lower())
    word_count = len(words_list)

    if not words_list:
        top_line = '- 0'
    else:
        counts = Counter(words_list)
        sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_word, count = sorted_words[0]
        top_line = f"{top_word} {count}"

    print(f'lines: {line_count}')
    print(f'words: {word_count}')
    print(f'top: {top_line}')

if __name__ == '__main__':
    main()