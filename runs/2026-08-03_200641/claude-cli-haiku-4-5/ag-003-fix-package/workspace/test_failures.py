#!/usr/bin/env python3
"""Test script to reproduce textstats failures."""

from textstats import summarize

print("Test 1: Empty input (should return {words: 0, unique: 0, avg_len: 0.0})")
try:
    result = summarize("")
    print(f"  Result: {result}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

print("\nTest 2: Only punctuation (should return {words: 0, unique: 0, avg_len: 0.0})")
try:
    result = summarize(".,;:!?\"'()")
    print(f"  Result: {result}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

print("\nTest 3: Case sensitivity (should count Dog and dog as same word)")
try:
    result = summarize("Dog dog DOG")
    print(f"  Result: {result}")
    print(f"  Expected: {{words: 3, unique: 1, avg_len: 3.0}}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

print("\nTest 4: Punctuation handling (should strip from Dog. and dog)")
try:
    result = summarize("Dog. dog")
    print(f"  Result: {result}")
    print(f"  Expected: {{words: 2, unique: 1, avg_len: 3.0}}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

print("\nTest 5: Multiple whitespace types (tabs, newlines, spaces)")
try:
    result = summarize("hello\tworld\nfoo  bar")
    print(f"  Result: {result}")
    print(f"  Expected: {{words: 4, unique: 4, avg_len: ...}}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

print("\nTest 6: Complex example")
try:
    result = summarize("The quick, brown fox!")
    print(f"  Result: {result}")
    print(f"  Expected: {{words: 4, unique: 4, avg_len: 4.25}}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
