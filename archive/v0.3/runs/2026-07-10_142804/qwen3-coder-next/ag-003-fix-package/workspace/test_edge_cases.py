#!/usr/bin/env python3
"""Additional edge case tests for textstats.summarize"""

from textstats import summarize

# Additional edge cases
tests = [
    # Whitespace only
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Punctuation with words - () are stripped, so both are 5 chars
    ("(Hello) world", {"words": 2, "unique": 2, "avg_len": 5.0}),  # (5+5)/2 = 5.0
    
    # Mixed punctuation
    ("...hello!!!", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Single word with punctuation
    ("Hello...", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Numbers as words (should count as words)
    ("123 456", {"words": 2, "unique": 2, "avg_len": 3.0}),
    
    # Empty string with spaces
    ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Newlines only between words
    ("\n\n\n", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("a\nb\nc", {"words": 3, "unique": 3, "avg_len": 1.0}),
    
    # Complex punctuation at boundaries (only spec'd punctuation)
    ('"""Hello"""', {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Multiple consecutive spaces/tabs/newlines
    ("a\t\t\tb\n\n\nc   d", {"words": 4, "unique": 4, "avg_len": 1.0}),
]

print("Additional edge case tests:\n")
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
    print("ALL EDGE CASE TESTS PASSED!")
else:
    print("Some tests failed.")
