"""Reproduce bugs in textstats.summarize."""
from textstats import summarize

# Bug 1: tokenize only splits on spaces, not any whitespace
print("=== Test 1: tabs and newlines ===")
result = summarize("hello\tworld\nfoo")
print(result)
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"

# Bug 2: case-insensitive unique count
print("\n=== Test 2: case-insensitive unique ===")
result = summarize("Dog. dog DOG")
print(result)
assert result["unique"] == 1, f"Expected 1 unique, got {result['unique']}"

# Bug 3: empty input should not raise
print("\n=== Test 3: empty input ===")
try:
    result = summarize("")
    print(result)
except ZeroDivisionError as e:
    print(f"ZeroDivisionError raised: {e}")

# Bug 4: only punctuation tokens shouldn't count
print("\n=== Test 4: only punctuation ===")
result = summarize("... ,,, !!!")
print(result)
assert result["words"] == 0, f"Expected 0 words, got {result['words']}"
assert result["unique"] == 0, f"Expected 0 unique, got {result['unique']}"

# Bug 5: avg_len rounding and punctuation stripping
print("\n=== Test 5: avg_len with punctuation ===")
result = summarize("Hello, world!")
print(result)
# "Hello" -> 5, "world" -> 5, avg = 5.0
assert result["avg_len"] == 5.0, f"Expected 5.0, got {result['avg_len']}"
