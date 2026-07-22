"""Reproduce bugs in textstats.summarize."""
from textstats import summarize

# Test 1: whitespace handling (tabs, newlines, multiple spaces)
r = summarize("hello\tworld\nfoo   bar")
print(f"Test 1 - multi-whitespace: {r}")
assert r["words"] == 4, f"Expected 4 words, got {r['words']}"

# Test 2: case-insensitive unique count
r = summarize("Dog. dog DOG!")
print(f"Test 2 - case insensitive: {r}")
assert r["unique"] == 1, f"Expected 1 unique, got {r['unique']}"

# Test 3: pure punctuation tokens should not count as words
r = summarize("... !!! ???")
print(f"Test 3 - pure punctuation: {r}")
assert r["words"] == 0, f"Expected 0 words, got {r['words']}"

# Test 4: empty input must not raise
r = summarize("")
print(f"Test 4 - empty: {r}")
assert r == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {r}"

# Test 5: avg_len rounding (hi=2, there=5 -> avg=3.5)
r = summarize("hi there")
print(f"Test 5 - avg_len: {r}")
assert r["avg_len"] == 3.5, f"Expected 3.5, got {r['avg_len']}"

# Test 6: mixed punctuation and words
r = summarize('"Hello," said the dog.')
print(f"Test 6 - mixed: {r}")
assert r["words"] == 4, f"Expected 4 words, got {r['words']}"
assert r["unique"] == 4, f"Expected 4 unique, got {r['unique']}"

# Test 7: avg_len rounding to 2 decimals
r = summarize("a bb ccc dddd")
print(f"Test 7 - round: {r}")
assert r["avg_len"] == 2.5, f"Expected 2.5, got {r['avg_len']}"

print("All tests passed!")
