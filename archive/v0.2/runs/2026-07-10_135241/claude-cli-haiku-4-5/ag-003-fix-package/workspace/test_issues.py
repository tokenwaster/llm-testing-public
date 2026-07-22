#!/usr/bin/env python3
"""Test script to reproduce the bugs."""

from textstats import summarize

# Test 1: Multiple whitespace (spaces, tabs, newlines)
print("Test 1: Multiple whitespace types")
text1 = "hello\tworld\n  foo"
result1 = summarize(text1)
print(f"  Input: {repr(text1)}")
print(f"  Result: {result1}")
print(f"  Expected: words=3, unique=3")
print()

# Test 2: Case-insensitive unique count
print("Test 2: Case-insensitive unique words")
text2 = "Dog dog DOG dog"
result2 = summarize(text2)
print(f"  Input: {repr(text2)}")
print(f"  Result: {result2}")
print(f"  Expected: words=4, unique=1")
print()

# Test 3: Punctuation stripping and case-insensitivity
print("Test 3: Punctuation and case-insensitivity combined")
text3 = "Dog. dog DOG, dog!"
result3 = summarize(text3)
print(f"  Input: {repr(text3)}")
print(f"  Result: {result3}")
print(f"  Expected: words=4, unique=1")
print()

# Test 4: Only punctuation should not count as word
print("Test 4: Punctuation-only tokens should not count")
text4 = "hello ... world"
result4 = summarize(text4)
print(f"  Input: {repr(text4)}")
print(f"  Result: {result4}")
print(f"  Expected: words=2, unique=2")
print()

# Test 5: Empty input should not raise
print("Test 5: Empty input")
text5 = ""
try:
    result5 = summarize(text5)
    print(f"  Input: {repr(text5)}")
    print(f"  Result: {result5}")
    print(f"  Expected: words=0, unique=0, avg_len=0.0")
except Exception as e:
    print(f"  ERROR: {e}")
print()

# Test 6: Only whitespace should return empty
print("Test 6: Only whitespace")
text6 = "   \t\n  "
try:
    result6 = summarize(text6)
    print(f"  Input: {repr(text6)}")
    print(f"  Result: {result6}")
    print(f"  Expected: words=0, unique=0, avg_len=0.0")
except Exception as e:
    print(f"  ERROR: {e}")
print()

# Test 7: Average length calculation
print("Test 7: Average length (two words 'hello' and 'world')")
text7 = "hello world"
result7 = summarize(text7)
print(f"  Input: {repr(text7)}")
print(f"  Result: {result7}")
print(f"  Expected: avg_len=5.0 (5+5)/2")
