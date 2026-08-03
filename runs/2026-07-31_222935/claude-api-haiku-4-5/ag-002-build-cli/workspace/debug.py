import re
from collections import Counter

content = "hello hello world\ntest test test\n"
text_lower = content.lower()
words = re.findall(r'[a-z]+', text_lower)
print("Words:", words)
word_counter = Counter(words)
print("Counter:", word_counter)
top_word, top_count = max(word_counter.items(), key=lambda x: (-x[1], x[0]))
print(f"Top: {top_word} {top_count}")
