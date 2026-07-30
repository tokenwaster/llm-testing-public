from textstats import summarize

# Test 1: Basic functionality
result = summarize("Hello world hello")
assert result == {"words": 3, "unique": 2, "avg_len": 5.0}, f"Test 1 failed: {result}"

# Test 2: Case-insensitive uniqueness
result = summarize("Dog dog DOG")
assert result == {"words": 3, "unique": 1, "avg_len": 3.0}, f"Test 2 failed: {result}"

# Test 3: Punctuation stripping
result = summarize("Dog. dog")
assert result == {"words": 2, "unique": 1, "avg_len": 3.0}, f"Test 3 failed: {result}"

# Test 4: Multiple whitespace (tabs, newlines, multiple spaces)
result = summarize("hello\tworld\n\nfoo  bar")
assert result == {"words": 4, "unique": 4, "avg_len": 4.0}, f"Test 4 failed: {result}"

# Test 5: Punctuation-only tokens should not count
result = summarize("... !!!")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Test 5 failed: {result}"

# Test 6: Empty input
result = summarize("")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Test 6 failed: {result}"

# Test 7: avg_len rounding
result = summarize("a bb ccc")
assert result == {"words": 3, "unique": 3, "avg_len": 2.0}, f"Test 7 failed: {result}"

# Test 8: Leading/trailing punctuation
result = summarize('"(hello)"')
assert result == {"words": 1, "unique": 1, "avg_len": 5.0}, f"Test 8 failed: {result}"

# Test 9: Mixed punctuation and case
result = summarize("Hello, hello! World? world.")
assert result == {"words": 4, "unique": 2, "avg_len": 5.0}, f"Test 9 failed: {result}"

print("All tests passed!")
