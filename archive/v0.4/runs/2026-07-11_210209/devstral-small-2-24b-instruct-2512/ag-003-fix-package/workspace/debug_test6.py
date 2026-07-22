#!/usr/bin/env python3
"""Debug script for test case 6."""

from textstats.helpers import tokenize, clean

test_text = ". , ; : ! ? ' ( ) "
print(f"Input: {repr(test_text)}")

tokens = tokenize(test_text)
print(f"Tokens: {tokens}")

cleaned = [clean(t) for t in tokens]
print(f"Cleaned: {cleaned}")

words = [c for c in cleaned if c]
print(f"Words (non-empty): {words}")
