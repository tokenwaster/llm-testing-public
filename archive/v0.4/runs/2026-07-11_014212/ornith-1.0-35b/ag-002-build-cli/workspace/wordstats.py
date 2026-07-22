import sys
from collections import Counter


def count_lines(content):
    """Count lines: split by newline, trailing final newline does not add extra line."""
    if content == '':
        return 0
    parts = content.split('\n')
    if parts[-1] == '':
        parts = parts[:-1]
    return len(parts)


def extract_words(content):
    """Extract words: maximal runs of ASCII letters after lowercasing."""
    text_lower = content.lower()
    words = []
    current_word = []
    for ch in text_lower:
        if 'a' <= ch <= 'z':
            current_word.append(ch)
        else:
            if current_word:
                words.append(''.join(current_word))
                current_word = []
    if current_word:
        words.append(''.join(current_word))
    return words


def main():
    path = sys.argv[1]

    with open(path, 'r') as f:
        content = f.read()

    line_count = count_lines(content)
    words = extract_words(content)
    word_count = len(words)

    print(f"lines: {line_count}")
    print(f"words: {word_count}")

    if word_count == 0:
        print("top: - 0")
    else:
        counter = Counter(words)
        max_count = max(counter.values())
        top_words = sorted([w for w, c in counter.items() if c == max_count])
        print(f"top: {top_words[0]} {max_count}")


if __name__ == '__main__':
    main()
