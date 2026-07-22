#!/usr/bin/env python3
"""Test script for textstats.summarize"""

from textstats import summarize

# Test cases
tests = [
    # Basic test
    ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Case-insensitive unique words
    ("Hello hello", {"words": 2, "unique": 1, "avg_len": 5.0}),
    
    # Punctuation stripping
    ("Hello, world!", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Multiple whitespace (spaces, tabs, newlines)
    ("Hello   world\t\nfoo", {"words": 3, "unique": 3, "avg_len": round((5+5+3)/3, 2)}),
    
    # Empty input
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Only punctuation
    ("!!!???", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Mixed with punctuation at edges
    ('"Hello" world', {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Dog/Dog. test from spec - both should be same word (case-insensitive)
    ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),  # "Dog" and "dog" both length 3
]

print("Running tests...")
passed = 0
failed = 0

for i, (text, expected) in enumerate(tests):
    result = summarize(text)
    print("\nTest %d: %r" % (i+1, text))
    print("  Expected: %s" % expected)
    print("  Got:      %s" % result)
    
    # Check all values
    try:
        if (result["words"] == expected["words"] and 
            result["unique"] == expected["unique"] and 
            abs(result.get("avg_len", 0) - expected["avg_len"]) <= 0.01):
            print("  PASS")
            passed += 1
        else:
            print("  FAIL")
            failed += 1
    except Exception as e:
        print("  ERROR: %s" % e)
        failed += 1

print("\n" + "="*50)
print("Results: %d passed, %d failed" % (passed, failed))
