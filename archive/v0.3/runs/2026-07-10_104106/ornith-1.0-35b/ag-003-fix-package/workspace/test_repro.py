"""Reproduce the bugs before fixing."""
from textstats import summarize

# Bug 1: tabs/newlines not treated as word separators
print("Test 1 - whitespace:")
result = summarize("hello\tworld\nfoo")
print(result)
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"

# Bug 2: empty input should return zeros, not raise ZeroDivisionError
print("Test 2 - empty:")
try:
    result = summarize("")
    print(result)
except Exception as e:
    print(f"RAISED: {type(e).__name__}: {e}")

# Bug 3: case-insensitive + punctuation stripping
print("Test 3 - case+punct:")
result = summarize('Dog. cat, dog "cat"')
print(result)
assert result["words"] == 4, f"Expected 4 words, got {result['words']}"
assert result["unique"] == 2, f"Expected 2 unique, got {result['unique']}"

# Bug 4: token that is only punctuation should not count
print("Test 4 - punctuation-only tokens:")
result = summarize('... !!! ???')
print(result)
assert result["words"] == 0, f"Expected 0 words, got {result['words']}"

# Bug 5: multiple spaces
print("Test 5 - multiple spaces:")
result = summarize("hello   world")
print(result)
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"
