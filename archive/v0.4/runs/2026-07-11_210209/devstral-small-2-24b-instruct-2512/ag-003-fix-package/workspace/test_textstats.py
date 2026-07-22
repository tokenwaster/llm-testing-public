#!/usr/bin/env python3
"""Test script for textstats package."""

from textstats import summarize

# Test cases based on specification
test_cases = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),  # Empty input
    ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),  # Simple case
    ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),  # Case insensitive with punctuation
    ("Hello... world!", {"words": 2, "unique": 2, "avg_len": 5.0}),  # Punctuation at end
    ("(Hello) [world]", {"words": 2, "unique": 2, "avg_len": 6.0}),  # Both tokens become words with different lengths
    (". , ; : ! ? ' ( ) ", {"words": 0, "unique": 0, "avg_len": 0.0}),  # Only specified punctuation as words
    ("The quick brown fox jumps over the lazy dog", {"words": 9, "unique": 8, "avg_len": 3.89}),  # "the" appears twice
    ("Hello hello HELLO", {"words": 3, "unique": 1, "avg_len": 5.0}),  # All same word different cases
    ("  Multiple   spaces   between   words  ", {"words": 4, "unique": 4, "avg_len": 6.5}),  # Multiple spaces
    ("Tab\tseparated\twords", {"words": 3, "unique": 3, "avg_len": 5.67}),  # Tabs
    ("Newline\nseparated\nwords", {"words": 3, "unique": 3, "avg_len": 7.0}),  # Newlines
]

print("Testing textstats.summarize():")
print("=" * 60)

for i, (input_text, expected) in enumerate(test_cases, 1):
    result = summarize(input_text)
    passed = result == expected
    status = "PASS" if passed else "FAIL"
    
    print(f"\nTest {i}: {status}")
    print(f"Input: {repr(input_text)}")
    print(f"Expected: {expected}")
    print(f"Got:      {result}")
    
    if not passed:
        print("  Differences:")
        for key in expected:
            if result[key] != expected[key]:
                print(f"    {key}: expected {expected[key]}, got {result[key]}")

print("\n" + "=" * 60)
print("Testing complete.")
