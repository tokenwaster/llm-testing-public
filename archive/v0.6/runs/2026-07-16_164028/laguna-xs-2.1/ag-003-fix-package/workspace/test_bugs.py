#!/usr/bin/env python3
"""Test script to reproduce bugs in textstats."""

from textstats import summarize

# Test 1: Empty input should not raise
print("Test 1: Empty input")
try:
    result = summarize("")
    print(f"  Result: {result}")
    assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected all zeros, got {result}"
    print("  PASS")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 2: Multiple whitespace types
print("\nTest 2: Multiple whitespace types (tabs, newlines)")
text = "hello\tworld\nfoo  bar"
result = summarize(text)
print(f"  Input: {repr(text)}")
print(f"  Result: {result}")
# Should have 4 words: hello, world, foo, bar
assert result["words"] == 4, f"Expected 4 words, got {result['words']}"
print("  PASS")

# Test 3: Case-insensitive unique count
print("\nTest 3: Case-insensitive unique count")
text = "Dog dog DOG"
result = summarize(text)
print(f"  Input: {repr(text)}")
print(f"  Result: {result}")
assert result["unique"] == 1, f"Expected 1 unique word, got {result['unique']}"
print("  PASS")

# Test 4: Punctuation stripping for unique count
print("\nTest 4: Punctuation stripping for unique count")
text = "Dog. dog, DOG!"
result = summarize(text)
print(f"  Input: {repr(text)}")
print(f"  Result: {result}")
assert result["unique"] == 1, f"Expected 1 unique word, got {result['unique']}"
print("  PASS")

# Test 5: Pure punctuation tokens should not count as words
print("\nTest 5: Pure punctuation tokens should not count as words")
text = "hello !!! world"
result = summarize(text)
print(f"  Input: {repr(text)}")
print(f"  Result: {result}")
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"
assert result["unique"] == 2, f"Expected 2 unique words, got {result['unique']}"
print("  PASS")

# Test 6: Average length calculation
print("\nTest 6: Average length calculation")
text = "a bb ccc"
result = summarize(text)
print(f"  Input: {repr(text)}")
print(f"  Result: {result}")
# avg_len = (1 + 2 + 3) / 3 = 2.0
assert result["avg_len"] == 2.0, f"Expected avg_len 2.0, got {result['avg_len']}"
print("  PASS")

# Test 7: Only whitespace input
print("\nTest 7: Only whitespace input")
text = "   \t\n  "
result = summarize(text)
print(f"  Input: {repr(text)}")
print(f"  Result: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected all zeros, got {result}"
print("  PASS")

# Test 8: Only punctuation input
print("\nTest 8: Only punctuation input")
text = "!!! ??? ..."
result = summarize(text)
print(f"  Input: {repr(text)}")
print(f"  Result: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected all zeros, got {result}"
print("  PASS")

# Test 9: Mixed case with different punctuation
print("\nTest 9: Mixed case with different punctuation")
text = "Hello, HELLO. hello!"
result = summarize(text)
print(f"  Input: {repr(text)}")
print(f"  Result: {result}")
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"
assert result["unique"] == 1, f"Expected 1 unique word, got {result['unique']}"
assert result["avg_len"] == 5.0, f"Expected avg_len 5.0, got {result['avg_len']}"
print("  PASS")

# Test 10: Parentheses and quotes in words
print("\nTest 10: Parentheses and quotes in words")
text = '"hello" (world)'
result = summarize(text)
print(f"  Input: {repr(text)}")
print(f"  Result: {result}")
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"
assert result["unique"] == 2, f"Expected 2 unique words, got {result['unique']}"
print("  PASS")

print("\nAll tests passed!")