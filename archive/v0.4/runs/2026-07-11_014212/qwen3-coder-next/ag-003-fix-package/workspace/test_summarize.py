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
    ('"Hello", world!', {"words": 2, "unique": 2, "avg_len": 5.0}),  # Hello=5, world=5, avg=5
    
    # Dog/Dog. test from spec
    ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),
    
    # Empty input
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Only punctuation - should not count as words
    ("!!! ??? ...", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Multiple whitespace (tabs, newlines)
    ("Hello\tworld\nfoo bar", {"words": 4, "unique": 4, "avg_len": 4.0}),  # 5+5+3+3=16/4=4
    
    # Mixed whitespace
    ("Hello   \t\n  world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Additional edge cases
    ("a b c d e", {"words": 5, "unique": 5, "avg_len": 1.0}),  # All single chars
    
    # Words with punctuation at both ends
    ('"Hello"', {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Mixed case with punctuation
    ('"HELLO", hello', {"words": 2, "unique": 1, "avg_len": 5.0}),
]

print("Testing summarize function:\n")
for i, (text, expected) in enumerate(tests, 1):
    try:
        result = summarize(text)
        passed = result == expected
        status = "[PASS]" if passed else "[FAIL]"
        print(f"Test {i}: {status}")
        print(f"  Input: {repr(text)}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        if not passed:
            # Check individual fields
            for key in ["words", "unique", "avg_len"]:
                if result.get(key) != expected.get(key):
                    print(f"    Mismatch on '{key}': expected {expected.get(key)}, got {result.get(key)}")
        print()
    except Exception as e:
        print(f"Test {i}: [ERROR] - {type(e).__name__}: {e}")
        print(f"  Input: {repr(text)}")
        print()
