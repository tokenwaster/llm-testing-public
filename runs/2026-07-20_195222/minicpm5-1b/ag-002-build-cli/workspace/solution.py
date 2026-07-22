import re
from collections import Counter

def count_words(text):
    # Count words: sequences of ASCII letters (a-z)
    words = re.findall(r'[a-z]+', text.lower())
    return len(words), Counter(words)

def wordstats(filename, args=[]):
    with open(filename, 'r') as f:
        content = f.read()
    
    lines, words = count_words(content)
    top_word, top_count = words.most_common(1)[0]
    
    print(f"lines: {lines}")
    print(f"words: {words}")
    print(f"top: {top_word} {top_count}")

if __name__ == "__main__":
    wordstats(__file__, filename="sample.txt")
