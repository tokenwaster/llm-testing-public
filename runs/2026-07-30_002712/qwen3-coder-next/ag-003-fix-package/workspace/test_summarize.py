from textstats import summarize

# Test 1: Basic functionality
result = summarize("Hello world")
print(f"Test 1 (basic): {result}")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Expected {{'words': 2, 'unique': 2, 'avg_len': 5.0}}, got {result}"

# Test 2: Case-insensitive uniqueness
result = summarize("Hello hello HELLO")
print(f"Test 2 (case-insensitive): {result}")
assert result == {"words": 3, "unique": 1, "avg_len": 5.0}, f"Expected {{'words': 3, 'unique': 1, 'avg_len': 5.0}}, got {result}"

# Test 3: Punctuation stripping
result = summarize("Dog. dog \"dog\" (dog)!")
print(f"Test 3 (punctuation): {result}")
assert result == {"words": 4, "unique": 1, "avg_len": 3.0}, f"Expected {{'words': 4, 'unique': 1, 'avg_len': 3.0}}, got {result}"

# Test 4: Multiple whitespace
result = summarize("Hello\tworld\nfoo   bar\t\nbaz")
print(f"Test 4 (multiple whitespace): {result}")
assert result == {"words": 5, "unique": 5, "avg_len": 3.8}, f"Expected {{'words': 5, 'unique': 5, 'avg_len': 3.8}}, got {result}"

# Test 5: Empty input
result = summarize("")
print(f"Test 5 (empty): {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected {{'words': 0, 'unique': 0, 'avg_len': 0.0}}, got {result}"

# Test 6: Only punctuation
result = summarize("!!!???...,,,'\"")
print(f"Test 6 (only punctuation): {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected {{'words': 0, 'unique': 0, 'avg_len': 0.0}}, got {result}"

# Test 7: Mixed with punctuation and case
result = summarize("One, two three! Four?")
print(f"Test 7 (mixed): {result}")
assert result == {"words": 4, "unique": 4, "avg_len": 3.75}, f"Expected {{'words': 4, 'unique': 4, 'avg_len': 3.75}}, got {result}"

print("\nAll tests passed!")
