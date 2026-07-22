from textstats import summarize

# Test 1: Basic functionality with multiple whitespace types
result = summarize("Hello   world\t\there")
print(f"Test 1 (multi-whitespace): {result}")
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"

# Test 2: Case-insensitive unique count
result = summarize("Dog. dog DOG.")
print(f"Test 2 (case-insensitive unique): {result}")
assert result["unique"] == 1, f"Expected 1 unique, got {result['unique']}"

# Test 3: Punctuation-only tokens don't count
result = summarize("...")
print(f"Test 3 (punctuation only): {result}")
assert result["words"] == 0, f"Expected 0 words, got {result['words']}"
assert result["unique"] == 0, f"Expected 0 unique, got {result['unique']}"

# Test 4: Empty input
result = summarize("")
print(f"Test 4 (empty): {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result}"

# Test 5: avg_len rounding
result = summarize("abc def ghi")
print(f"Test 5 (avg_len): {result}")
assert result["avg_len"] == 3.0, f"Expected 3.0, got {result['avg_len']}"

# Test 6: Punctuation stripping - "Dog." should be length 3 not 4
result = summarize("Dog.")
print(f"Test 6 (strip punctuation): {result}")
assert result["words"] == 1 and result["unique"] == 1, f"Got {result}"

# Test 7: No words -> avg_len must not raise
try:
    result = summarize("... ...")
    print(f"Test 7 (no words no crash): {result}")
except ZeroDivisionError as e:
    print(f"FAIL - ZeroDivisionError: {e}")

print("\nAll tests passed!")
