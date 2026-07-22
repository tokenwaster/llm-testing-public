#!/usr/bin/env python3
"""Additional edge case tests for textstats.summarize"""

from textstats import summarize

# Additional edge cases
tests = [
    # Single word with punctuation
    ("Hello!", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Punctuation only at start and end
    ("(Hello)", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Mixed punctuation
    ("...Hello!!!", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Words with internal punctuation (should keep internal punctuation as part of word)
    ("don't", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Multiple punctuations at boundaries
    ('"""Hello"""', {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Newlines and spaces mixed
    ("Hello\nworld\ntest", {"words": 3, "unique": 3, "avg_len": 4.67}),
    
    # Tabs only
    ("\t\t\t", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Empty string with newline
    ("\n", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Single character words
    ("a b c", {"words": 3, "unique": 3, "avg_len": 1.0}),
    
    # Mixed case with punctuation
    ("HeLLo, hello, HELLO!", {"words": 3, "unique": 1, "avg_len": 5.0}),
]

print("Additional edge case tests...")
for i, (text, expected) in enumerate(tests, 1):
    try:
        result = summarize(text)
        passed = result == expected
        status = "PASS" if passed else "FAIL"
        print("\nTest %d: %s" % (i, status))
        print("  Input: %r" % text)
        print("  Expected: %s" % expected)
        print("  Got:      %s" % result)
    except Exception as e:
        print("\nTest %d: ERROR" % i)
        print("  Input: %r" % text)
        print("  Error: %s: %s" % (type(e).__name__, e))
