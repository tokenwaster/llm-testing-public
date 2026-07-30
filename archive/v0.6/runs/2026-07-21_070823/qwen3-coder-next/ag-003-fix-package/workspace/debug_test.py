#!/usr/bin/env python3
from textstats import summarize
from textstats.helpers import tokenize, clean

text = "hello\tworld\nfoo"
print(f"Input: {repr(text)}")
tokens = tokenize(text)
print(f"Tokens: {tokens}")
cleaned = [clean(t) for t in tokens]
print(f"Cleaned: {cleaned}")
words = [c for c in cleaned if c]
print(f"Words: {words}")
for w in words:
    print(f"  '{w}' len={len(w)}")
