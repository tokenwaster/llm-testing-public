#!/usr/bin/env python3
"""Test script for textstats.summarize"""

from textstats import summarize

# Test cases
tests = [
    # Basic test
    ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Empty input
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Only whitespace
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Case insensitive
    ("Hello hello", {"words": 2, "unique": 1, "avg_len": 5.0}),
    
    # Punctuation stripping
    ("Hello, world!", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Mixed punctuation and case
    ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),
    
    # Multiple whitespace
    ("Hello   \t\n  world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Only punctuation (should not count as words)
    ("!!! ??? ...", {"words": 0, "unique": 0, "avg_len": 0.0}),
]

print("Running tests...")
for i, (text, expected) in enumerate(tests):
    result = summarize(text)
    passed = result == expected
    status = "PASS" if passed else "FAIL"
    print("\nTest %d: %s" % (i+1, status))
    print("  Input: %r" % text)
    print("  Expected: %s" % expected)
    print("  Got:      %s" % result)
    if not passed:
        # Show what's different
        for key in expected:
            if result.get(key) != expected[key]:
                print("  Mismatch on '%s': expected %s, got %s" % (key, expected[key], result.get(key)))

print("\nDone!")
