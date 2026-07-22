"""Test script to reproduce bugs in textstats."""
from textstats import summarize

# Test 1: whitespace handling (tabs, newlines, multiple spaces)
print("Test 1 - whitespace:")
result = summarize("hello  world\tfoo\nbar")
print(f"  Input: 'hello  world\\tfoo\\nbar'")
print(f"  Result: {result}")
print(f"  Expected: words=4, unique=4, avg_len around 4.0")
print()

# Test 2: case-insensitive unique
print("Test 2 - case-insensitive:")
result = summarize("Dog dog DOG")
print(f"  Input: 'Dog dog DOG'")
print(f"  Result: {result}")
print(f"  Expected: words=3, unique=1")
print()

# Test 3: punctuation stripping
print("Test 3 - punctuation:")
result = summarize("Hello, world! 'How' (are) you?")
print(f"  Input: \"Hello, world! 'How' (are) you?\"")
print(f"  Result: {result}")
print(f"  Expected: words=5, unique=5")
print()

# Test 4: Dog. vs dog
print("Test 4 - Dog. vs dog:")
result = summarize("Dog. dog")
print(f"  Input: 'Dog. dog'")
print(f"  Result: {result}")
print(f"  Expected: words=2, unique=1")
print()

# Test 5: empty input
print("Test 5 - empty input:")
result = summarize("")
print(f"  Input: ''")
print(f"  Result: {result}")
print(f"  Expected: words=0, unique=0, avg_len=0.0")
print()

# Test 6: only punctuation
print("Test 6 - only punctuation:")
result = summarize("... !!! ???")
print(f"  Input: '... !!! ???'")
print(f"  Result: {result}")
print(f"  Expected: words=0, unique=0, avg_len=0.0")
print()

# Test 7: mixed punctuation and words
print("Test 7 - mixed:")
result = summarize("(hello) 'world'...")
print(f"  Input: \"(hello) 'world'...\"")
print(f"  Result: {result}")
print(f"  Expected: words=2, unique=2")