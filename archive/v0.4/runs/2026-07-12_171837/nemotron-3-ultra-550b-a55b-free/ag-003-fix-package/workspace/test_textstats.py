from textstats import summarize

# Test 1: Basic functionality
print("Test 1: Basic")
result = summarize("Hello world")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")

# Test 2: Multiple whitespace (tabs, newlines)
print("\nTest 2: Multiple whitespace")
result = summarize("Hello\tworld\nfoo  bar")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 4, 'unique': 4, 'avg_len': 4.0}}")

# Test 3: Case insensitivity
print("\nTest 3: Case insensitivity")
result = summarize("Dog dog DOG")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 3, 'unique': 1, 'avg_len': 3.0}}")

# Test 4: Punctuation stripping
print("\nTest 4: Punctuation stripping")
result = summarize("Dog. dog, DOG!")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 3, 'unique': 1, 'avg_len': 3.0}}")

# Test 5: Only punctuation tokens
print("\nTest 5: Only punctuation tokens")
result = summarize("Hello ... world")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")

# Test 6: Empty input
print("\nTest 6: Empty input")
result = summarize("")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")

# Test 7: Only punctuation
print("\nTest 7: Only punctuation")
result = summarize("... !!! ???")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")

# Test 8: Mixed punctuation and words
print("\nTest 8: Mixed punctuation and words")
result = summarize("Hello, world! How are you?")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 5, 'unique': 5, 'avg_len': 4.0}}")

# Test 9: Average length rounding
print("\nTest 9: Average length rounding")
result = summarize("a bb ccc")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 3, 'unique': 3, 'avg_len': 2.0}}")

# Test 10: Leading/trailing whitespace
print("\nTest 10: Leading/trailing whitespace")
result = summarize("  Hello world  ")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")