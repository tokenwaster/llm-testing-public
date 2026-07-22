from textstats import summarize

# Test 1: Multiple whitespace (tabs, newlines, multiple spaces)
print("Test 1 - Multiple whitespace:")
result = summarize("hello   world\t\nfoo")
print(f"  Result: {result}")
# hello(5) + world(5) + foo(3) = 13/3 = 4.33
print(f"  Expected: words=3, unique=3, avg_len=4.33")
assert result == {"words": 3, "unique": 3, "avg_len": 4.33}

# Test 2: Case-insensitive unique count
print("\nTest 2 - Case-insensitive unique:")
result = summarize("Dog dog DOG")
print(f"  Result: {result}")
print(f"  Expected: words=3, unique=1, avg_len=3.0")
assert result == {"words": 3, "unique": 1, "avg_len": 3.0}

# Test 3: Empty input
print("\nTest 3 - Empty input:")
result = summarize("")
print(f"  Result: {result}")
print(f"  Expected: words=0, unique=0, avg_len=0.0")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}

# Test 4: Only punctuation tokens
print("\nTest 4 - Only punctuation:")
result = summarize("... !!! ???")
print(f"  Result: {result}")
print(f"  Expected: words=0, unique=0, avg_len=0.0")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}

# Test 5: Punctuation stripping
print("\nTest 5 - Punctuation stripping:")
result = summarize('"Hello," said "world."')
print(f"  Result: {result}")
# "Hello," -> hello, said -> said, "world." -> world => 3 words
# hello(5) + said(4) + world(5) = 14/3 = 4.67
print(f"  Expected: words=3, unique=3, avg_len=4.67")
assert result == {"words": 3, "unique": 3, "avg_len": 4.67}

# Test 6: Whitespace-only input
print("\nTest 6 - Whitespace-only input:")
result = summarize("   \t\n  ")
print(f"  Result: {result}")
print(f"  Expected: words=0, unique=0, avg_len=0.0")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}

# Test 7: Mixed punctuation and words
print("\nTest 7 - Mixed punctuation and words:")
result = summarize("Hello, world! How are you?")
print(f"  Result: {result}")
# hello(5) + world(5) + how(3) + are(3) + you(3) = 19/5 = 3.8
print(f"  Expected: words=5, unique=5, avg_len=3.8")
assert result == {"words": 5, "unique": 5, "avg_len": 3.8}

print("\nAll tests passed!")
