#!/usr/bin/env python3
"""Additional edge case tests for textstats.summarize"""

from textstats import summarize

# Additional edge cases
tests = [
    # Single word with punctuation
    ("Hello!", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Punctuation only in middle (should not be stripped)
    ("don't", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Leading and trailing punctuation
    ('"Hello"', {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Mixed case with punctuation
    ("HeLLo, woRLD!", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Repeated same word with different punctuation
    ("Hello... hello??? HELLO!!!", {"words": 3, "unique": 1, "avg_len": 5.0}),
    
    # Newlines and tabs
    ("line1\nline2\tline3\r\nline4", {"words": 4, "unique": 4, "avg_len": 6.0}),
    
    # Single character words
    ("a b c", {"words": 3, "unique": 3, "avg_len": 1.0}),
    
    # Very long text
    ("word " * 1000, {"words": 1000, "unique": 1, "avg_len": 4.0}),
]

print("Running edge case tests...")
for i, (text, expected) in enumerate(tests):
    result = summarize(text)
    passed = result == expected
    status = "PASS" if passed else "FAIL"
    print("\nTest %d: %s" % (i+1, status))
    print("  Input: %r" % text[:50] + ("..." if len(text) > 50 else ""))
    print("  Expected: %s" % expected)
    print("  Got:      %s" % result)

print("\nDone!")
