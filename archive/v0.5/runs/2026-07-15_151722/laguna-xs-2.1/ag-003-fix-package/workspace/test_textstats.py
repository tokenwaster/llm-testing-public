#!/usr/bin/env python3
"""Test script to verify textstats bugs."""

from textstats import summarize

# Test 1: Basic functionality
print("Test 1: Basic functionality")
result = summarize("hello world")
print(f"  summarize('hello world') = {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")
assert result == {'words': 2, 'unique': 2, 'avg_len': 5.0}, "FAIL"
print("  PASS")
print()

# Test 2: Case-insensitive unique count
print("Test 2: Case-insensitive unique count")
result = summarize("Dog dog DOG")
print(f"  summarize('Dog dog DOG') = {result}")
print(f"  Expected: {{'words': 3, 'unique': 1, 'avg_len': 3.0}}")
assert result == {'words': 3, 'unique': 1, 'avg_len': 3.0}, "FAIL"
print("  PASS")
print()

# Test 3: Punctuation handling
print("Test 3: Punctuation handling")
result = summarize('Dog. "cat" (bird)')
print(f"  summarize('Dog. \"cat\" (bird)') = {result}")
# Dog. -> Dog (3), "cat" -> cat (3), (bird) -> bird (4)
# avg = (3+3+4)/3 = 3.33
print(f"  Expected: {{'words': 3, 'unique': 3, 'avg_len': 3.33}}")
assert result == {'words': 3, 'unique': 3, 'avg_len': 3.33}, "FAIL"
print("  PASS")
print()

# Test 4: Multiple whitespace
print("Test 4: Multiple whitespace")
result = summarize("hello   world\ttest\nnew")
print(f"  summarize('hello   world\\ttest\\nnew') = {result}")
# hello (5), world (5), test (4), new (3)
# avg = (5+5+4+3)/4 = 4.25
print(f"  Expected: {{'words': 4, 'unique': 4, 'avg_len': 4.25}}")
assert result == {'words': 4, 'unique': 4, 'avg_len': 4.25}, "FAIL"
print("  PASS")
print()

# Test 5: Empty input
print("Test 5: Empty input")
result = summarize("")
print(f"  summarize('') = {result}")
print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
assert result == {'words': 0, 'unique': 0, 'avg_len': 0.0}, "FAIL"
print("  PASS")
print()

# Test 6: Only punctuation
print("Test 6: Only punctuation")
result = summarize("... !!! ???")
print(f"  summarize('... !!! ???') = {result}")
print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
assert result == {'words': 0, 'unique': 0, 'avg_len': 0.0}, "FAIL"
print("  PASS")
print()

# Test 7: Mixed content with punctuation-only tokens
print("Test 7: Mixed content with punctuation-only tokens")
result = summarize("hello ... world !!!")
print(f"  summarize('hello ... world !!!') = {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")
assert result == {'words': 2, 'unique': 2, 'avg_len': 5.0}, "FAIL"
print("  PASS")
print()

# Test 8: Spec example - Dog. and dog are the same word
print("Test 8: Spec example - Dog. and dog are the same word")
result = summarize('Dog. dog')
print(f"  summarize('Dog. dog') = {result}")
# Dog. -> Dog (3), dog -> dog (3)
# avg = (3+3)/2 = 3.0
print(f"  Expected: {{'words': 2, 'unique': 1, 'avg_len': 3.0}}")
assert result == {'words': 2, 'unique': 1, 'avg_len': 3.0}, "FAIL"
print("  PASS")
print()

print("All tests passed!")