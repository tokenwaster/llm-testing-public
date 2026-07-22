#!/usr/bin/env python3
"""Test script to reproduce failures in textstats."""

from textstats import summarize

# Test 1: Multiple whitespace types
print("Test 1: Multiple whitespace types")
result = summarize("hello\tworld\nfoo  bar")
print(f"  Input: 'hello\\tworld\\nfoo  bar'")
print(f"  Result: {result}")
print(f"  Expected: words=4, unique=4, avg_len=4.0")
print()

# Test 2: Case insensitivity
print("Test 2: Case insensitivity")
result = summarize("Dog dog DOG")
print(f"  Input: 'Dog dog DOG'")
print(f"  Result: {result}")
print(f"  Expected: words=3, unique=1, avg_len=3.0")
print()

# Test 3: Punctuation stripping
print("Test 3: Punctuation stripping")
result = summarize("Dog. dog, DOG!")
print(f"  Input: 'Dog. dog, DOG!'")
print(f"  Result: {result}")
print(f"  Expected: words=3, unique=1, avg_len=3.0")
print()

# Test 4: Only punctuation tokens
print("Test 4: Only punctuation tokens")
result = summarize("hello ... world !!!")
print(f"  Input: 'hello ... world !!!'")
print(f"  Result: {result}")
print(f"  Expected: words=2, unique=2, avg_len=5.0")
print()

# Test 5: Empty input
print("Test 5: Empty input")
result = summarize("")
print(f"  Input: ''")
print(f"  Result: {result}")
print(f"  Expected: words=0, unique=0, avg_len=0.0")
print()

# Test 6: Input with only punctuation
print("Test 6: Input with only punctuation")
result = summarize("... !!! ???")
print(f"  Input: '... !!! ???'")
print(f"  Result: {result}")
print(f"  Expected: words=0, unique=0, avg_len=0.0")
print()

# Test 7: Average length rounding
print("Test 7: Average length rounding")
result = summarize("a bb ccc")
print(f"  Input: 'a bb ccc'")
print(f"  Result: {result}")
print(f"  Expected: words=3, unique=3, avg_len=2.0")
print()

# Test 8: Mixed case with punctuation
print("Test 8: Mixed case with punctuation")
result = summarize("Hello, WORLD! hello world.")
print(f"  Input: 'Hello, WORLD! hello world.'")
print(f"  Result: {result}")
print(f"  Expected: words=4, unique=2, avg_len=5.0")
print()