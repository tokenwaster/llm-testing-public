import re
from collections import Counter

def process_text(content):
    # Lines
    if not content:
        lines = 0
    else:
        if content.endswith('\n'):
            lines = content.count('\n')
        else:
            lines = content.count('\n') + 1

    # Words
    words = re.findall(r'[a-z]+', content.lower())
    
    total_words = len(words)
    
    counts = Counter(words)
    if not counts:
        top_word = "-"
        top_count = 0
    else:
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))
        
    return lines, total_words, top_word, top_count

# Tests
tests = [
    ("", (0, 0, "-", 0)),
    ("\n", (1, 0, "-", 0)),
    ("abc", (1, 1, "abc", 1)),
    ("abc\n", (1, 1, "abc", 1)),
    ("abc\ndef", (2, 2, "abc", 1)),
    ("abc\ndef\n", (2, 2, "abc", 1)),
    ("abc\n\n", (2, 1, "abc", 1)),
    ("apple banana apple", (1, 3, "apple", 2)),
    ("banana apple banana", (1, 3, "banana", 2)),
    ("apple banana", (1, 2, "apple", 1)),
    ("banana apple", (1, 2, "apple", 1)),
    ("123_abc!!def", (1, 2, "abc", 1)),
    ("ABC def", (1, 2, "abc", 1)),
]

for i, (text, expected) in enumerate(tests):
    result = process_text(text)
    assert result == expected, f"Test {i} failed: expected {expected}, got {result} for text {repr(text)}"
print("All tests passed!")
