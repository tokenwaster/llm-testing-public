from textstats import summarize

# Test 1: Basic functionality
result = summarize("hello world")
print(f"Test 1 - 'hello world': {result}")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Expected {{'words': 2, 'unique': 2, 'avg_len': 5.0}}, got {result}"

# Test 2: Case-insensitive unique words
result = summarize("Dog dog DOG")
print(f"Test 2 - 'Dog dog DOG': {result}")
assert result == {"words": 3, "unique": 1, "avg_len": 3.0}, f"Expected {{'words': 3, 'unique': 1, 'avg_len': 3.0}}, got {result}"

# Test 3: Punctuation stripping
result = summarize("Dog.")
print(f"Test 3 - 'Dog.': {result}")
assert result == {"words": 1, "unique": 1, "avg_len": 3.0}, f"Expected {{'words': 1, 'unique': 1, 'avg_len': 3.0}}, got {result}"

# Test 4: Punctuation-only token (should not count)
result = summarize("!!! hello")
print(f"Test 4 - '!!! hello': {result}")
assert result == {"words": 1, "unique": 1, "avg_len": 5.0}, f"Expected {{'words': 1, 'unique': 1, 'avg_len': 5.0}}, got {result}"

# Test 5: Multiple whitespaces (tabs, newlines)
result = summarize("hello\t\nworld")
print(f"Test 5 - 'hello\\t\\nworld': {result}")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Expected {{'words': 2, 'unique': 2, 'avg_len': 5.0}}, got {result}"

# Test 6: Empty input
result = summarize("")
print(f"Test 6 - empty string: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected {{'words': 0, 'unique': 0, 'avg_len': 0.0}}, got {result}"

# Test 7: Only punctuation (no words)
result = summarize("!!! ??? ...")
print(f"Test 7 - only punctuation: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected {{'words': 0, 'unique': 0, 'avg_len': 0.0}}, got {result}"

print("All tests passed!")