#!/usr/bin/env python3
"""Test script to reproduce failures in textstats."""

from textstats import summarize

# Test 1: Multiple whitespace types
print("Test 1: Multiple whitespace types")
result = summarize("hello\tworld\nfoo  bar")
print(f"  Input: 'hello\\tworld\\nfoo  bar'")
print(f"  Result: {result}")
print(f"  Expected words: 4, got: {result['words']}")

# Test 2: Case insensitivity
print("\nTest 2: Case insensitivity")
result = summarize("Dog dog DOG")
print(f"  Input: 'Dog dog DOG'")
print(f"  Result: {result}")
print(f"  Expected unique: 1, got: {result['unique']}")

# Test 3: Punctuation stripping
print("\nTest 3: Punctuation stripping")
result = summarize("Dog. dog, DOG!")
print(f"  Input: 'Dog. dog, DOG!'")
print(f"  Result: {result}")
print(f"  Expected unique: 1, got: {result['unique']}")

# Test 4: Only punctuation tokens
print("\nTest 4: Only punctuation tokens")
result = summarize("hello ... world")
print(f"  Input: 'hello ... world'")
print(f"  Result: {result}")
print(f"  Expected words: 2, got: {result['words']}")

# Test 5: Empty input
print("\nTest 5: Empty input")
result = summarize("")
print(f"  Input: ''")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")

# Test 6: Input with only punctuation
print("\nTest 6: Input with only punctuation")
result = summarize("... !!! ???")
print(f"  Input: '... !!! ???'")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")

# Test 7: Average length calculation
print("\nTest 7: Average length")
result = summarize("a bb ccc")
print(f"  Input: 'a bb ccc'")
print(f"  Result: {result}")
print(f"  Expected avg_len: 2.0, got: {result['avg_len']}")

# Test 8: Newlines and tabs
print("\nTest 8: Newlines and tabs")
result = summarize("hello\nworld\tfoo")
print(f"  Input: 'hello\\nworld\\tfoo'")
print(f"  Result: {result}")
print(f"  Expected words: 3, got: {result['words']}")