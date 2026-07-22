#!/usr/bin/env python3
"""Additional edge case tests for textstats.summarize"""

from textstats import summarize

# Additional edge cases
tests = [
    # Punctuation only in the middle (should not be stripped)
    ("don't stop", {"words": 2, "unique": 2, "avg_len": 4.0}),  # don't -> don't (punct in middle stays)
    
    # Leading and trailing punctuation
    ("'quoted'", {"words": 1, "unique": 1, "avg_len": 6.0}),
    
    # Multiple punctuations
    ("!!!hello!!!", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Newlines and tabs
    ("line1\nline2\tline3", {"words": 3, "unique": 3, "avg_len": 5.67}),
    
    # Mixed empty tokens after split
    ("a  b   c", {"words": 3, "unique": 3, "avg_len": 1.0}),
]

print("Running edge case tests...")
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
