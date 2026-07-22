#!/usr/bin/env python3
"""Test script for textstats.summarize"""

from textstats import summarize

# Test cases
tests = [
    # Basic test
    ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Case-insensitive unique words
    ("Hello hello HELLO", {"words": 3, "unique": 1, "avg_len": 5.0}),
    
    # Punctuation stripping
    ('"Hello", world!', {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Dog/Dog. test from spec
    ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),
    
    # Empty input
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Only punctuation
    ("!!!???", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Multiple whitespace (tabs, newlines)
    ("Hello\tworld\nfoo", {"words": 3, "unique": 3, "avg_len": 4.33}),  # (5+5+3)/3 = 4.33
    
    # Mixed whitespace
    ("Hello   world\t\tfoo\n\nbar", {"words": 4, "unique": 4, "avg_len": 4.0}),  # (5+5+3+3)/4 = 4.0
    
    # Additional edge cases
    ("a b c", {"words": 3, "unique": 3, "avg_len": 1.0}),
    ("test... test", {"words": 2, "unique": 1, "avg_len": 4.0}),  # "test" stripped to 4 chars
]

print("Testing summarize function:\n")
all_passed = True
for i, (text, expected) in enumerate(tests, 1):
    result = summarize(text)
    passed = result == expected
    all_passed = all_passed and passed
    status = "PASS" if passed else "FAIL"
    print(f"Test {i}: {status}")
    print(f"  Input: {repr(text)}")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")
    if not passed:
        # Show what went wrong
        from textstats.helpers import tokenize, clean
        tokens = tokenize(text)
        cleaned = [clean(t) for t in tokens]
        words = [c.lower() for c in cleaned if c]
        print(f"  Debug - tokens: {tokens}")
        print(f"  Debug - cleaned: {cleaned}")
        print(f"  Debug - words: {words}")
    print()

print("=" * 50)
if all_passed:
    print("ALL TESTS PASSED!")
else:
    print("Some tests failed.")
