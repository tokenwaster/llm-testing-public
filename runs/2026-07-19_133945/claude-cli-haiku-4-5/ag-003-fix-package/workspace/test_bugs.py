#!/usr/bin/env python3
"""Reproduction script for textstats bugs."""

from textstats import summarize

# Test 1: Multiple whitespace (spaces, tabs, newlines)
print("Test 1: Multiple whitespace")
result = summarize("hello\t\nworld  test")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 3, 'unique': 3, 'avg_len': 5.0}}")
print()

# Test 2: Case-insensitive uniqueness
print("Test 2: Case-insensitive uniqueness")
result = summarize("Dog dog DOG")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 3, 'unique': 1, 'avg_len': 3.0}}")
print()

# Test 3: Punctuation stripping
print("Test 3: Punctuation stripping")
result = summarize("Hello, world! How's \"it\"?")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 4, 'unique': 4, 'avg_len': 3.5}}")
print()

# Test 4: Empty input
print("Test 4: Empty input")
try:
    result = summarize("")
    print(f"  Result: {result}")
    print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
print()

# Test 5: Only punctuation
print("Test 5: Only punctuation")
try:
    result = summarize(".,;:!?\"'()")
    print(f"  Result: {result}")
    print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
