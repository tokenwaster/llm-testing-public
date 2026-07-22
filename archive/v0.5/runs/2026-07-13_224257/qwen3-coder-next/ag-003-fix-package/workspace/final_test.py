#!/usr/bin/env python3
"""Final verification of textstats.summarize()"""

from textstats import summarize

# Test 1: Basic functionality
result = summarize("Hello world")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Test 1 failed: {result}"
print("[PASS] Test 1")

# Test 2: Case-insensitive unique words
result = summarize("Dog dog DOG")
assert result == {"words": 3, "unique": 1, "avg_len": 3.0}, f"Test 2 failed: {result}"
print("[PASS] Test 2")

# Test 3: Words with punctuation (.,;:!?"'())
result = summarize("Hello, world!")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Test 3 failed: {result}"
print("[PASS] Test 3")

# Test 4: Multiple whitespace (tabs, newlines)
result = summarize("Hello\tworld\nfoo bar")
assert result == {"words": 4, "unique": 4, "avg_len": 4.0}, f"Test 4 failed: {result}"
print("[PASS] Test 4")

# Test 5: Empty string
result = summarize("")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Test 5 failed: {result}"
print("[PASS] Test 5")

# Test 6: Only punctuation (no words)
result = summarize("!?.:,")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Test 6 failed: {result}"
print("[PASS] Test 6")

# Test 7: Punctuation-only tokens mixed with words
result = summarize("Hello ! world ? foo , bar")
assert result == {"words": 4, "unique": 4, "avg_len": 4.0}, f"Test 7 failed: {result}"
print("[PASS] Test 7")

# Test 8: Leading and trailing punctuation from spec
result = summarize('"Hello", \'world\' (foo)')
assert result == {"words": 3, "unique": 3, "avg_len": 5.0}, f"Test 8 failed: {result}"
print("[PASS] Test 8")

# Test 9: Multiple spaces/tabs/newlines
result = summarize("Hello   \t\t\n\n  world")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Test 9 failed: {result}"
print("[PASS] Test 9")

# Test 10: Mixed case with punctuation
result = summarize("Dog, dog! DOG?")
assert result == {"words": 3, "unique": 1, "avg_len": 3.0}, f"Test 10 failed: {result}"
print("[PASS] Test 10")

# Test 11: Single word
result = summarize("Hello")
assert result == {"words": 1, "unique": 1, "avg_len": 5.0}, f"Test 11 failed: {result}"
print("[PASS] Test 11")

# Test 12: Word with only leading punctuation
result = summarize('"hello" world')
assert result == {"words": 2, "unique": 2, "avg_len": 6.0}, f"Test 12 failed: {result}"
print("[PASS] Test 12")

# Test 13: Word with only trailing punctuation
result = summarize("hello! world")
assert result == {"words": 2, "unique": 2, "avg_len": 6.0}, f"Test 13 failed: {result}"
print("[PASS] Test 13")

# Test 14: Average rounded to 2 decimals
result = summarize("a bb ccc")
assert result == {"words": 3, "unique": 3, "avg_len": 2.0}, f"Test 14 failed: {result}"
print("[PASS] Test 14")

# Test 15: Average rounded to 2 decimals (non-integer)
result = summarize("a bb")
assert result == {"words": 2, "unique": 2, "avg_len": 1.5}, f"Test 15 failed: {result}"
print("[PASS] Test 15")

print("\nAll tests passed!")
