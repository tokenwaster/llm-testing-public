#!/usr/bin/env python3
"""Test script to reproduce textstats bugs."""

from textstats import summarize

print("Test 1: Multiple whitespace")
result = summarize("hello  world\nfoo\t\tbar")
print(f"  Result: {result}")
print(f"  Expected words: 4, got: {result['words']}")
print()

print("Test 2: Case-insensitive unique words")
result = summarize("Dog dog DOG cat Cat")
print(f"  Result: {result}")
print(f"  Expected unique: 2, got: {result['unique']}")
print()

print("Test 3: Punctuation handling")
result = summarize("Dog. dog \"dog\" (dog)")
print(f"  Result: {result}")
print(f"  Expected unique: 1, got: {result['unique']}")
print()

print("Test 4: Empty input")
try:
    result = summarize("")
    print(f"  Result: {result}")
    print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
except ZeroDivisionError as e:
    print(f"  ERROR: ZeroDivisionError - {e}")
print()

print("Test 5: Only punctuation")
try:
    result = summarize(".,;!?")
    print(f"  Result: {result}")
    print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
except ZeroDivisionError as e:
    print(f"  ERROR: ZeroDivisionError - {e}")
print()

print("Test 6: Average word length")
result = summarize("hi hello world")
print(f"  Result: {result}")
# "hi" = 2, "hello" = 5, "world" = 5, avg = (2+5+5)/3 = 12/3 = 4.0
print(f"  Expected avg_len: 4.0, got: {result['avg_len']}")
