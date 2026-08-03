#!/usr/bin/env python3
"""Test script to verify textstats.summarize behavior."""

from textstats import summarize

# Test 1: Basic test with various whitespace
text1 = "Hello world! How are you? I'm fine."
result1 = summarize(text1)
print(f"Test 1 (basic): {result1}")
expected_words = 6  # Hello, world, How, are, you, I, m, fine -> but wait let's count properly: "Hello", "world!", "How", "are", "you?", "I'm", "fine." 
# After cleaning and lowercasing for unique? Let me think...
# The words after cleaning (lowercased would be): hello, world, how, are, you, i'm, fine -> 7 words.

# Actually the spec says: words = total word count of cleaned words that aren't empty.
# Cleaned means punctuation stripped from ends only, not removing internal punctuation. So "I'm" becomes "I'm". That's one word.

print("\nExpected for text1:")
print("words should be 7 (hello, world, how, are, you, i'm, fine)")
print("unique should be 7 if case-insensitive")
print(f"actual: words={result1['words']}, unique={result1['unique']}")

# Test 2: Case insensitivity for unique count
text2 = "Hello HELLO hello HELLOWORLD"
result2 = summarize(text2)
print(f"\nTest 2 (case): {result2}")
print("Expected words=4, unique=1 (all 'hello' or similar after lowercasing? Wait: hellobworld is different)")
# Actually cleaned versions: hello, HELLO, hello, HELLOWORLD -> if case-insensitive: hello, hello, hello, helloworld -> 2 unique.

print("\nExpected words=4")
if result2['unique'] == 2:
    print("PASS unique=2 (case insensitive)")
else:
    print(f"FAIL unique should be 2 but got {result2['unique']}")

# Test 3: Multiple whitespace types
text3 = "word1\tword2\nword3   word4\r\nword5"
result3 = summarize(text3)
print(f"\nTest 3 (whitespace): {result3}")
print("Expected words=5, unique=5")

# Test 4: Punctuation-only tokens should not count
text4 = "... ,, ! ?"
result4 = summarize(text4)
print(f"\nTest 4 (punct only): {result4}")
print("Expected words=0, unique=0, avg_len=0.0")

# Test 5: Empty input
text5 = ""
result5 = summarize(text5)
print(f"\nTest 5 (empty): {result5}")
print("Expected words=0, unique=0, avg_len=0.0")

# Test 6: Leading/trailing punctuation stripping works correctly
text6 = ".,Hello., ;World; .!"
result6 = summarize(text6)
print(f"\nTest 6 (punct strip): {result6}")
print("Expected words=2, unique=2, avg_len=(5+5)/2=5.0")
