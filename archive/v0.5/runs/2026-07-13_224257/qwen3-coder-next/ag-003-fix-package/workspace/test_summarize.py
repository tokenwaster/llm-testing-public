#!/usr/bin/env python3
"""Test script for textstats.summarize()"""

from textstats import summarize

# Test cases
print("Test 1: Basic text")
result = summarize("Hello world")
print(f"Result: {result}")
print(f"Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")
print()

print("Test 2: Case-insensitive unique words")
result = summarize("Dog dog DOG")
print(f"Result: {result}")
print(f"Expected: {{'words': 3, 'unique': 1, 'avg_len': 3.0}}")
print()

print("Test 3: Words with punctuation")
result = summarize("Hello, world!")
print(f"Result: {result}")
print(f"Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")
print()

print("Test 4: Multiple whitespace (tabs, newlines)")
result = summarize("Hello\tworld\nfoo bar")
print(f"Result: {result}")
print(f"Expected: {{'words': 4, 'unique': 4, 'avg_len': 4.75}}")
print()

print("Test 5: Empty string")
result = summarize("")
print(f"Result: {result}")
print(f"Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
print()

print("Test 6: Only punctuation (no words)")
result = summarize("!?.:,")
print(f"Result: {result}")
print(f"Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
print()

print("Test 7: Punctuation-only tokens mixed with words")
result = summarize("Hello ! world ? foo , bar")
print(f"Result: {result}")
print(f"Expected: {{'words': 4, 'unique': 4, 'avg_len': 4.75}}")
print()

print("Test 8: Leading and trailing punctuation")
result = summarize('"Hello", \'world\' (foo) [bar]')
print(f"Result: {result}")
print(f"Expected: {{'words': 4, 'unique': 4, 'avg_len': 4.75}}")
print()
