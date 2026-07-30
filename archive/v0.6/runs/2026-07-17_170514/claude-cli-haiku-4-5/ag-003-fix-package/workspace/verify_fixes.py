#!/usr/bin/env python
"""Verify all fixes work correctly."""

from textstats import summarize

print("Edge cases verification:")
print()

print("1. Mixed whitespace:")
result = summarize("hello   \t\n  world")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Failed: {result}"
print(f"   {result} OK")

print("2. Case insensitivity with punctuation:")
result = summarize("Hello, HELLO, hello.")
assert result == {"words": 3, "unique": 1, "avg_len": 5.0}, f"Failed: {result}"
print(f"   {result} OK")

print("3. Only whitespace:")
result = summarize("   \t\n  ")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Failed: {result}"
print(f"   {result} OK")

print("4. All punctuation:")
result = summarize(".,!?;:()'\"")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Failed: {result}"
print(f"   {result} OK")

print("5. Single word:")
result = summarize("Hello")
assert result == {"words": 1, "unique": 1, "avg_len": 5.0}, f"Failed: {result}"
print(f"   {result} OK")

print()
print("All edge cases passed!")
