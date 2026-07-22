#!/usr/bin/env python3
"""Test script for textstats.summarize"""

from textstats import summarize

# Test cases
tests = [
    # Basic test
    ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Case insensitivity
    ("Hello hello", {"words": 2, "unique": 1, "avg_len": 5.0}),
    
    # Punctuation stripping
    ('"Hello", world!', {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Empty input
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Only whitespace
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Only punctuation (no words)
    ("!!!???", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Multiple whitespace
    ("Hello   world\t\ntest", {"words": 3, "unique": 3, "avg_len": 4.67}),
    
    # Word with punctuation at both ends
    ('(Dog.)', {"words": 1, "unique": 1, "avg_len": 3.0}),
    
    # Mixed case with punctuation
    ("Hello, HELLO, hello", {"words": 3, "unique": 1, "avg_len": 5.0}),
    
    # Single word
    ("Test", {"words": 1, "unique": 1, "avg_len": 4.0}),
]

print("Running tests...")
for i, (text, expected) in enumerate(tests, 1):
    try:
        result = summarize(text)
        passed = result == expected
        status = "[PASS]" if passed else "[FAIL]"
        print("\nTest %d: %s" % (i, status))
        print("  Input: %r" % text)
        print("  Expected: %s" % expected)
        print("  Got:      %s" % result)
    except Exception as e:
        print("\nTest %d: [ERROR]" % i)
        print("  Input: %r" % text)
        print("  Error: %s" % e)
