"""Reproduce bugs before fixing."""
from textstats import summarize

# Bug 1: tabs/newlines not handled as word separators
print("Test 1 - whitespace handling:")
result = summarize("hello\tworld\nfoo")
print(f"  Result: {result}")
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"

# Bug 2: empty input causes ZeroDivisionError
print("Test 2 - empty input:")
try:
    result = summarize("")
    print(f"  Result: {result}")
except ZeroDivisionError as e:
    print(f"  FAILED with ZeroDivisionError")

# Bug 3: case-insensitive + punctuation stripping
print("Test 3 - case & punctuation:")
result = summarize('Dog. cat, dog "cat"!')
print(f"  Result: {result}")
assert result["words"] == 4, f"Expected 4 words, got {result['words']}"
assert result["unique"] == 2, f"Expected 2 unique, got {result['unique']}"

# Bug 4: pure punctuation tokens should not count
print("Test 4 - pure punctuation:")
result = summarize("... !!! ???")
print(f"  Result: {result}")
assert result["words"] == 0, f"Expected 0 words, got {result['words']}"

# Bug 5: avg_len rounding (2+2+3)/3 = 2.33
print("Test 5 - avg_len rounding:")
result = summarize("ab cd efg")
print(f"  Result: {result}")
assert result["avg_len"] == 2.33, f"Expected 2.33, got {result['avg_len']}"

# Bug 6: multiple whitespace in a row
print("Test 6 - multiple whitespace:")
result = summarize("  hello   world  ")
print(f"  Result: {result}")
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"

# Bug 7: only punctuation (no actual words)
print("Test 7 - only punctuation:")
result = summarize("...")
print(f"  Result: {result}")
assert result["avg_len"] == 0.0, f"Expected 0.0, got {result['avg_len']}"

print("\nAll tests passed!")
