#!/usr/bin/env python3
"""Trace Test 3"""

from textstats.helpers import tokenize, clean

text = '"Hello", world!'
print("Input: %r" % text)

tokens = tokenize(text)
print("Tokens: %s" % tokens)

cleaned = [clean(t) for t in tokens]
print("Cleaned: %s" % cleaned)

words = [c.lower() for c in cleaned if c]
print("Words (lowercase): %s" % words)

if words:
    avg_len = round(sum(len(w) for w in words) / len(words), 2)
    print("Avg length: %.2f" % avg_len)
else:
    print("No words!")

# Let me check what the expected value should be
print("\nManual calculation:")
for i, w in enumerate(words):
    print("  Word %d: %s (length %d)" % (i+1, w, len(w)))
if words:
    total = sum(len(w) for w in words)
    avg = total / len(words)
    print("Total length: %d" % total)
    print("Average: %.2f" % avg)
