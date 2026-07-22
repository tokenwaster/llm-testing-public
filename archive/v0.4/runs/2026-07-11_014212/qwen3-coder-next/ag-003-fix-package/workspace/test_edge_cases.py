#!/usr/bin/env python3
"""Additional edge case tests"""

from textstats import summarize

# More edge cases
tests = [
    # Whitespace only
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Single word with punctuation
    ("Hello...", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Punctuation only in middle (should not be stripped)
    ("don't", {"words": 1, "unique": 1, "avg_len": 5.0}),  # apostrophe in middle stays
    
    # Multiple consecutive punctuation
    ("Hello!!! world???", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Mixed with newlines
    ("\n\nLine1\nLine2\t\tLine3\n", {"words": 3, "unique": 3, "avg_len": 5.0}),
    
    # Very long text
    ("word " * 100, {"words": 100, "unique": 1, "avg_len": 4.0}),
]

print("Additional edge case tests:\n")
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
            for key in ["words", "unique", "avg_len"]:
                if result.get(key) != expected.get(key):
                    print(f"    Mismatch on '{key}': expected {expected.get(key)}, got {result.get(key)}")
        print()
    except Exception as e:
        print(f"Test {i}: [ERROR] - {type(e).__name__}: {e}")
        print()
