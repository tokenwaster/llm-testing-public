#!/usr/bin/env python3
"""Debug script to understand the cleaning process."""

from textstats.helpers import tokenize, clean

test_text = "(Hello) [world]"
print(f"Input: {repr(test_text)}")

tokens = tokenize(test_text)
print(f"Tokens: {tokens}")

cleaned = [clean(t) for t in tokens]
print(f"Cleaned: {cleaned}")

words = [c for c in cleaned if c]
print(f"Words: {words}")

for word in words:
    print(f"  '{word}' has length {len(word)}")

avg_len = round(sum(len(w) for w in words) / len(words), 2)
print(f"Average length: {avg_len}")
