"""Reproduce bugs in textstats.summarize."""
from textstats import summarize

# Bug 1: tokenize doesn't handle tabs/newlines/multiple whitespace
print("=== Test 1: Whitespace handling ===")
result = summarize("hello\tworld\nfoo   bar")
print(result)
assert result["words"] == 4, f"Expected 4 words, got {result['words']}"

# Bug 2: unique is case-sensitive
print("\n=== Test 2: Case-insensitive unique ===")
result = summarize("Dog. dog DOG!")
print(result)
assert result["unique"] == 1, f"Expected 1 unique word, got {result['unique']}"

# Bug 3: empty input should not raise
print("\n=== Test 3: Empty input ===")
try:
    result = summarize("")
    print(result)
    assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result}"
except Exception as e:
    print(f"RAISED: {e}")

# Bug 4: punctuation-only tokens should not count
print("\n=== Test 4: Punctuation only ===")
result = summarize("... !!! ???")
print(result)
assert result["words"] == 0, f"Expected 0 words, got {result['words']}"

# Bug 5: avg_len rounding (2+2+4)/3 = 2.67
print("\n=== Test 5: avg_len rounding ===")
result = summarize("ab cd efgh")
print(result)
assert result["avg_len"] == 2.67, f"Expected 2.67, got {result['avg_len']}"

# Bug 6: leading/trailing punctuation stripping
print("\n=== Test 6: Punctuation stripping ===")
result = summarize('"Hello," "hello."')
print(result)
assert result["unique"] == 1, f"Expected 1 unique word, got {result['unique']}"

# Extra: mixed whitespace + case + punctuation
print("\n=== Test 7: Full integration ===")
result = summarize("The quick\tbrown fox\njumps over   the lazy dog.")
print(result)
assert result["words"] == 9, f"Expected 9 words, got {result['words']}"
assert result["unique"] == 8, f"Expected 8 unique (the appears twice), got {result['unique']}"

print("\nAll tests passed!")
