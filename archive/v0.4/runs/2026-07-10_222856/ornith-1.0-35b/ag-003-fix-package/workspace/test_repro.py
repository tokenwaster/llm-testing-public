"""Reproduce bugs in textstats."""
from textstats import summarize

# Test 1: tabs and newlines as separators
print("Test 1 - whitespace handling:")
result = summarize("hello\tworld\nfoo")
print(f"  Result: {result}")
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"

# Test 2: multiple spaces in a row
print("Test 2 - multiple spaces:")
result = summarize("hello   world")
print(f"  Result: {result}")
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"

# Test 3: case-insensitive unique count with punctuation stripping
print("Test 3 - case/punctuation:")
result = summarize('Dog. and "dog"!')
print(f"  Result: {result}")
assert result["unique"] == 2, f"Expected 2 unique words (dog, and), got {result['unique']}"

# Test 4: empty input should not raise
print("Test 4 - empty input:")
try:
    result = summarize("")
    print(f"  Result: {result}")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 5: only punctuation tokens
print("Test 5 - only punctuation:")
result = summarize('... !!! ???')
print(f"  Result: {result}")
assert result["words"] == 0, f"Expected 0 words, got {result['words']}"
assert result["unique"] == 0, f"Expected 0 unique, got {result['unique']}"

# Test 6: avg_len rounding
print("Test 6 - avg_len:")
result = summarize("ab cd efg")
print(f"  Result: {result}")
expected_avg = round((2 + 2 + 3) / 3, 2)
assert result["avg_len"] == expected_avg, f"Expected {expected_avg}, got {result['avg_len']}"

# Test 7: leading/trailing punctuation stripping
print("Test 7 - punctuation stripping:")
result = summarize("'Hello,' world!")
print(f"  Result: {result}")
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"

# Test 8: avg_len uses cleaned (punctuation-stripped) lengths
print("Test 8 - avg_len with punctuation:")
result = summarize('Dog. cat')
print(f"  Result: {result}")
assert result["avg_len"] == round((3 + 3) / 2, 2), f"Expected 3.0, got {result['avg_len']}"

# Test 9: whitespace-only input
print("Test 9 - whitespace only:")
try:
    result = summarize("   \t\n  ")
    print(f"  Result: {result}")
except Exception as e:
    print(f"  ERROR: {e}")
