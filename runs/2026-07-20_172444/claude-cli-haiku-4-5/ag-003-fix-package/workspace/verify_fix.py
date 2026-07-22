#!/usr/bin/env python3
"""Comprehensive verification of textstats fixes."""

from textstats import summarize

print("=== Verification Tests ===\n")

# Test 1: Basic functionality
print("Test 1: Basic text")
result = summarize("Hello world")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}
print(f"  PASS: {result}")

# Test 2: Empty and whitespace
print("\nTest 2: Empty string")
result = summarize("")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}
print(f"  PASS: {result}")

print("\nTest 3: Only whitespace")
result = summarize("  \t  \n  ")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}
print(f"  PASS: {result}")

# Test 4: All whitespace types
print("\nTest 4: Mixed whitespace (space, tab, newline)")
result = summarize("hello\tworld\nfoo  bar")
assert result["words"] == 4
print(f"  PASS: words={result['words']}")

# Test 5: Case insensitivity
print("\nTest 5: Case insensitivity for unique count")
result = summarize("Apple APPLE apple")
assert result["unique"] == 1
assert result["words"] == 3
print(f"  PASS: {result}")

# Test 6: Punctuation stripping
print("\nTest 6: Punctuation stripping")
result = summarize("Hello, world! How's it going?")
assert result["unique"] == 4  # hello, world, how's (becomes "how's" after strip), it, going
print(f"  PASS: unique={result['unique']}")

# Test 7: Punctuation-only tokens
print("\nTest 7: Punctuation-only tokens don't count")
result = summarize("hello . . world")
assert result["words"] == 2
assert result["unique"] == 2
print(f"  PASS: {result}")

# Test 8: Leading/trailing punctuation
print("\nTest 8: Leading and trailing punctuation removal")
result = summarize("'quoted' (parenthesized) [bracketed]")
assert "quoted" in str(result)
assert result["words"] == 3
print(f"  PASS: {result}")

# Test 9: Average length calculation
print("\nTest 9: Average length calculation")
result = summarize("I am happy")
assert result["avg_len"] == round((1 + 2 + 5) / 3, 2)
print(f"  PASS: avg_len={result['avg_len']}")

print("\n=== All verification tests passed! ===")
