#!/usr/bin/env python3
"""Trace edge cases"""

from textstats.helpers import tokenize, clean

# Test "don't stop"
text = "don't stop"
print("Test: %r" % text)
tokens = tokenize(text)
cleaned = [clean(t) for t in tokens]
words = [c.lower() for c in cleaned if c]
print("  Words: %s" % words)
for w in words:
    print("    %s (len=%d)" % (w, len(w)))
if words:
    avg = round(sum(len(w) for w in words) / len(words), 2)
    print("  Avg: %.2f" % avg)

print()

# Test 'line1\nline2\tline3'
text = 'line1\nline2\tline3'
print("Test: %r" % text)
tokens = tokenize(text)
cleaned = [clean(t) for t in tokens]
words = [c.lower() for c in cleaned if c]
print("  Words: %s" % words)
for w in words:
    print("    %s (len=%d)" % (w, len(w)))
if words:
    avg = round(sum(len(w) for w in words) / len(words), 2)
    print("  Avg: %.2f" % avg)
