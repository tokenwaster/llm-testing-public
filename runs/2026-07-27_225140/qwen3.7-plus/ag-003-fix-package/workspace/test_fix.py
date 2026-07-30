from textstats import summarize

# Test 1: Basic functionality
result = summarize("Hello world hello")
print("Test 1:", result)
assert result == {"words": 3, "unique": 2, "avg_len": 5.0}, f"FAIL: {result}"

# Test 2: Multiple whitespace (tabs, newlines)
result = summarize("Hello\tworld\n\nfoo   bar")
print("Test 2:", result)
assert result == {"words": 4, "unique": 4, "avg_len": 4.0}, f"FAIL: {result}"

# Test 3: Punctuation stripping and case-insensitive
result = summarize("Dog. dog DOG")
print("Test 3:", result)
assert result == {"words": 3, "unique": 1, "avg_len": 3.0}, f"FAIL: {result}"

# Test 4: Empty input
result = summarize("")
print("Test 4:", result)
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"FAIL: {result}"

# Test 5: Only punctuation tokens
result = summarize("... !!!")
print("Test 5:", result)
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"FAIL: {result}"

# Test 6: Mixed punctuation and words
result = summarize("Hello, world!")
print("Test 6:", result)
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"FAIL: {result}"

# Test 7: None-like whitespace only
result = summarize("   \t\n  ")
print("Test 7:", result)
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"FAIL: {result}"

print("All tests passed!")
