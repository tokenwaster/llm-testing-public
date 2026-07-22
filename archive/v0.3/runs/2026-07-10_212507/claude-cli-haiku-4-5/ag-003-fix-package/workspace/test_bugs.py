#!/usr/bin/env python3
"""Test script to reproduce bugs in textstats."""

from textstats import summarize

# Test 1: Multiple spaces (should split into words)
print("Test 1: Multiple spaces")
result = summarize("hello  world   test")
print(f"  Input: 'hello  world   test'")
print(f"  Expected: {{'words': 3, 'unique': 3, 'avg_len': 4.67}}")
print(f"  Got:      {result}")
print()

# Test 2: Tabs and newlines
print("Test 2: Tabs and newlines")
result = summarize("hello\tworld\ntest")
print(f"  Input: 'hello\\tworld\\ntest'")
print(f"  Expected: {{'words': 3, 'unique': 3, 'avg_len': 4.67}}")
print(f"  Got:      {result}")
print()

# Test 3: Punctuation handling
print("Test 3: Punctuation - case insensitive and strip punct")
result = summarize("Dog. dog DOG")
print(f"  Input: 'Dog. dog DOG'")
print(f"  Expected: {{'words': 3, 'unique': 1, 'avg_len': 3.0}}")
print(f"  Got:      {result}")
print()

# Test 4: Punctuation-only tokens
print("Test 4: Punctuation-only tokens")
result = summarize("hello , world")
print(f"  Input: 'hello , world'")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")
print(f"  Got:      {result}")
print()

# Test 5: Empty input
print("Test 5: Empty input")
try:
    result = summarize("")
    print(f"  Input: ''")
    print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
    print(f"  Got:      {result}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
print()

# Test 6: Only punctuation
print("Test 6: Only punctuation")
try:
    result = summarize(".,;:!?\"'()")
    print(f"  Input: '.,;:!?\"'()'")
    print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
    print(f"  Got:      {result}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
