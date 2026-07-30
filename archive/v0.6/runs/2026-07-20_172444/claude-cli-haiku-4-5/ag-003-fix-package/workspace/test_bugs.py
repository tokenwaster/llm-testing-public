#!/usr/bin/env python3
"""Test script to reproduce textstats bugs."""

from textstats import summarize

# Test 1: Empty input should not crash
print("Test 1: Empty input")
try:
    result = summarize("")
    print(f"  OK Result: {result}")
    assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected empty dict, got {result}"
except Exception as e:
    print(f"  ERROR: {e}")

# Test 2: Whitespace-only input should not crash
print("\nTest 2: Whitespace-only input")
try:
    result = summarize("   \t\n  ")
    print(f"  OK Result: {result}")
    assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected empty dict, got {result}"
except Exception as e:
    print(f"  ERROR: {e}")

# Test 3: Multiple whitespace types should split correctly
print("\nTest 3: Multiple whitespace types (spaces, tabs, newlines)")
result = summarize("hello\tworld\nfoo  bar")
print(f"  Result: {result}")
expected_words = 4
print(f"  Expected words: {expected_words}, got: {result['words']}")

# Test 4: Case-insensitive unique count
print("\nTest 4: Case-insensitive unique count")
result = summarize("Dog dog DOG")
print(f"  Result: {result}")
print(f"  Expected unique: 1, got: {result['unique']}")

# Test 5: Punctuation handling
print("\nTest 5: Punctuation handling")
result = summarize("Dog. dog \"dog\"")
print(f"  Result: {result}")
print(f"  Expected unique: 1, got: {result['unique']}")

# Test 6: Punctuation-only tokens should not count
print("\nTest 6: Punctuation-only tokens should not count")
result = summarize("hello . world")
print(f"  Result: {result}")
print(f"  Expected words: 2, got: {result['words']}")

# Test 7: Average length calculation
print("\nTest 7: Average length calculation")
result = summarize("a bb ccc")
print(f"  Result: {result}")
expected_avg_len = (1 + 2 + 3) / 3
print(f"  Expected avg_len: {round(expected_avg_len, 2)}, got: {result['avg_len']}")
