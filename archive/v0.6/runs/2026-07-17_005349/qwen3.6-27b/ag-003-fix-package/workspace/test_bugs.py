"""Test script to reproduce the bugs."""
from textstats import summarize

# Test 1: Multiple whitespace (tabs, newlines, multiple spaces)
text1 = "hello   world\t\nfoo"
result1 = summarize(text1)
print(f"Test 1 (whitespace): {result1}")
print(f"  Expected: words=3, unique=3, avg_len=3.67")

# Test 2: Case-insensitive unique
text2 = "Dog dog DOG"
result2 = summarize(text2)
print(f"Test 2 (case-insensitive): {result2}")
print(f"  Expected: words=3, unique=1, avg_len=3.0")

# Test 3: Empty input
text3 = ""
result3 = summarize(text3)
print(f"Test 3 (empty): {result3}")
print(f"  Expected: words=0, unique=0, avg_len=0.0")

# Test 4: Only punctuation
text4 = "!!! ... ,,, "
result4 = summarize(text4)
print(f"Test 4 (only punctuation): {result4}")
print(f"  Expected: words=0, unique=0, avg_len=0.0")

# Test 5: Punctuation stripping
text5 = "Hello, world! How are you?"
result5 = summarize(text5)
print(f"Test 5 (punctuation): {result5}")
print(f"  Expected: words=5, unique=5, avg_len=3.4")
