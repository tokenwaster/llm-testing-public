from textstats import summarize

# Test 1: Empty input
result = summarize("")
print(f"Empty input: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Failed: {result}"

# Test 2: Words separated by tabs and newlines
result = summarize("hello\tworld\nfoo")
print(f"Tab/newline separated: {result}")
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"

# Test 3: Multiple consecutive spaces
result = summarize("hello   world")
print(f"Multiple spaces: {result}")
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"

# Test 4: Case-insensitive unique + punctuation stripping
result = summarize("Dog. dog DOG")
print(f"Case/punctuation: {result}")
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"
assert result["unique"] == 1, f"Expected 1 unique, got {result['unique']}"

# Test 5: Punctuation-only tokens should not count
result = summarize("... ,,, !!!")
print(f"Punctuation only: {result}")
assert result["words"] == 0, f"Expected 0 words, got {result['words']}"

# Test 6: avg_len calculation
result = summarize("hi there")
print(f"avg_len: {result}")
assert result["avg_len"] == 3.5, f"Expected 3.5, got {result['avg_len']}"

# Test 7: Leading/trailing punctuation on words
result = summarize("'Hello,' world!")
print(f"Punctuation on words: {result}")
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"
assert result["unique"] == 2, f"Expected 2 unique, got {result['unique']}"

print("\nAll tests passed!")
