#!/usr/bin/env python3
from textstats import summarize

print("Comprehensive verification:")
print()

# Basic case
result = summarize("Hello world")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Failed: {result}"
print("[PASS] Basic case")

# Case-insensitive
result = summarize("Dog DOG dog")
assert result == {"words": 3, "unique": 1, "avg_len": 3.0}, f"Failed: {result}"
print("[PASS] Case-insensitive")

# Multiple whitespace types
result = summarize("a  b\tc\nd")
assert result == {"words": 4, "unique": 4, "avg_len": 1.0}, f"Failed: {result}"
print("[PASS] Multiple whitespace types")

# Punctuation stripping
result = summarize("Hello, world! How's it?")
assert result["words"] == 4 and result["unique"] == 4, f"Failed: {result}"
print("[PASS] Punctuation stripping")

# Punctuation-only tokens
result = summarize("hello . . world")
assert result["words"] == 2 and result["unique"] == 2, f"Failed: {result}"
print("[PASS] Punctuation-only tokens ignored")

# Empty and whitespace-only
result = summarize("")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Failed: {result}"
print("[PASS] Empty input")

result = summarize("   \t\n  ")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Failed: {result}"
print("[PASS] Whitespace-only input")

# Complex punctuation
result = summarize("It's (really) great!")
cleaned_words = ["it's", "really", "great"]  # after strip and lowercase
assert result["words"] == 3, f"Failed word count: {result}"
print("[PASS] Complex punctuation")

print()
print("All tests passed!")
