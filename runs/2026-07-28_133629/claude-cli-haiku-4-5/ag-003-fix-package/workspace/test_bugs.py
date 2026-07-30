#!/usr/bin/env python3
from textstats import summarize

# Test 1: Multiple spaces (should be treated as one separator)
print("Test 1: Multiple spaces")
result = summarize("hello  world")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")
print()

# Test 2: Tabs and newlines
print("Test 2: Tabs and newlines")
result = summarize("hello\tworld\nfoo")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 3, 'unique': 3, 'avg_len': 4.67}}")
print()

# Test 3: Case-insensitive and punctuation
print("Test 3: Case-insensitive (Dog vs dog)")
result = summarize("Dog. dog")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 2, 'unique': 1, 'avg_len': 3.0}}")
print()

# Test 4: Punctuation-only tokens
print("Test 4: Punctuation-only tokens")
result = summarize("hello . world")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.5}}")
print()

# Test 5: Empty input
print("Test 5: Empty input")
result = summarize("")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
print()

# Test 6: Only punctuation
print("Test 6: Only punctuation")
result = summarize(".,;")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
