#!/usr/bin/env python3
"""Debug punctuation handling"""

from textstats.helpers import tokenize, clean

# Test punctuation stripping
text = '"Hello", world!'
tokens = tokenize(text)
print(f"Tokens: {tokens}")
cleaned = [clean(t) for t in tokens]
print(f"Cleaned: {cleaned}")

# Check what happens with each token
for t in tokens:
    c = clean(t)
    print(f"  {repr(t)} -> {repr(c)} (len={len(c)})")
