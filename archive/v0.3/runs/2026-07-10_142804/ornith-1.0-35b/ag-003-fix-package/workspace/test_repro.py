"""Reproduce the bugs before fixing."""
from textstats import summarize

# Bug 1: tokenize only splits on spaces, not any whitespace
print("=== Test tabs/newlines ===")
result = summarize("hello\tworld\nfoo")
print(result)
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"

# Bug 2: unique should be case-insensitive
print("\n=== Test case-insensitive unique ===")
result = summarize("Dog. dog DOG")
print(result)
assert result["unique"] == 1, f"Expected 1 unique, got {result['unique']}"

# Bug 3: empty input must not raise
print("\n=== Test empty input ===")
try:
    result = summarize("")
    print(result)
    assert result == {"words": 0, "unique": 0, "avg_len": 0.0}
except ZeroDivisionError as e:
    print(f"ZeroDivisionError raised: {e}")

# Bug 4: punctuation-only tokens should not count
print("\n=== Test punctuation only ===")
result = summarize("... !!! ???")
print(result)
assert result["words"] == 0, f"Expected 0 words, got {result['words']}"

# Bug 5: multiple spaces create empty tokens
print("\n=== Test multiple spaces ===")
result = summarize("hello   world")
print(result)
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"
