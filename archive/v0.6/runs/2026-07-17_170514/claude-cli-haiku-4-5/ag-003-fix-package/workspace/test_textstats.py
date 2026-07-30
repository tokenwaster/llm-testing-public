#!/usr/bin/env python
"""Test script to reproduce textstats bugs."""

from textstats import summarize

print("Test 1: Multiple spaces (should split on any whitespace)")
result = summarize("hello  world   test")
print(f"  Result: {result}")
print(f"  Expected words: 3, got: {result['words']}")
print()

print("Test 2: Tabs and newlines (should split on any whitespace)")
result = summarize("hello\tworld\ntest")
print(f"  Result: {result}")
print(f"  Expected words: 3, got: {result['words']}")
print()

print("Test 3: Case-insensitive unique count")
result = summarize("Dog dog DOG")
print(f"  Result: {result}")
print(f"  Expected unique: 1, got: {result['unique']}")
print()

print("Test 4: Punctuation stripping in unique count")
result = summarize("Dog. dog \"dog\"")
print(f"  Result: {result}")
print(f"  Expected unique: 1, got: {result['unique']}")
print()

print("Test 5: Pure punctuation tokens ignored")
result = summarize("hello . . . world")
print(f"  Result: {result}")
print(f"  Expected words: 2, got: {result['words']}")
print()

print("Test 6: Empty input (should not raise)")
try:
    result = summarize("")
    print(f"  Result: {result}")
    print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
print()

print("Test 7: Average length calculation")
result = summarize("a bb ccc")
print(f"  Result: {result}")
print(f"  Expected avg_len: 2.0 (1+2+3)/3, got: {result['avg_len']}")
print()

print("Test 8: Only punctuation (should not raise)")
try:
    result = summarize(".,;!?")
    print(f"  Result: {result}")
    print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
