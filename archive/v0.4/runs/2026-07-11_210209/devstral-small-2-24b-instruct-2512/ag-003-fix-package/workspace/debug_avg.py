#!/usr/bin/env python3
"""Debug script for average length calculation."""

from textstats.helpers import tokenize, clean

test_cases = [
    "  Multiple   spaces   between   words  ",
    "Tab\tseparated\twords",
    "Newline\nseparated\nwords"
]

for test_text in test_cases:
    print(f"Input: {repr(test_text)}")
    
    tokens = tokenize(test_text)
    print(f"Tokens: {tokens}")
    
    cleaned = [clean(t) for t in tokens]
    print(f"Cleaned: {cleaned}")
    
    words = [c for c in cleaned if c]
    print(f"Words: {words}")
    
    lengths = [len(w) for w in words]
    print(f"Lengths: {lengths}")
    print(f"Sum of lengths: {sum(lengths)}")
    print(f"Number of words: {len(words)}")
    
    avg_len = round(sum(len(w) for w in words) / len(words), 2)
    print(f"Average length: {avg_len}")
    print()
