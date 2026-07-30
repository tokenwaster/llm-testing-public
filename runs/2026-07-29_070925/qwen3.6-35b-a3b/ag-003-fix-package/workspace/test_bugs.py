from textstats import summarize

# Test 1: Basic functionality
result = summarize("Hello world")
print(f"Test 1 (basic): {result}")
assert result["words"] == 2, f"Expected words=2, got {result['words']}"
assert result["unique"] == 2, f"Expected unique=2, got {result['unique']}"
print("  PASS")

# Test 2: Case insensitive unique
result = summarize("Dog dog DOG")
print(f"Test 2 (case): {result}")
assert result["unique"] == 1, f"Expected unique=1, got {result['unique']}"
print("  PASS")

# Test 3: Punctuation stripping
result = summarize("Dog. hello, world!")
print(f"Test 3 (punct): {result}")
assert result["unique"] == 2, f"Expected unique=2, got {result['unique']}"
print("  PASS")

# Test 4: Tabs and newlines as separators
result = summarize("hello\tworld\nfoo")
print(f"Test 4 (whitespace): {result}")
assert result["words"] == 3, f"Expected words=3, got {result['words']}"
print("  PASS")

# Test 5: Multiple consecutive spaces
result = summarize("hello   world")
print(f"Test 5 (multi-space): {result}")
assert result["words"] == 2, f"Expected words=2, got {result['words']}"
print("  PASS")

# Test 6: Empty input
result = summarize("")
print(f"Test 6 (empty): {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result}"
print("  PASS")

# Test 7: Only punctuation
result = summarize("... !!!")
print(f"Test 7 (punct only): {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result}"
print("  PASS")

# Test 8: avg_len calculation
result = summarize("ab cd efg")
print(f"Test 8 (avg_len): {result}")
assert result["avg_len"] == 2.6, f"Expected avg_len=2.6, got {result['avg_len']}"
print("  PASS")

print("\nAll tests passed!")
