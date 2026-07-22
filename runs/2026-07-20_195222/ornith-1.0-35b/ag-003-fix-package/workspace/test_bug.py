"""Quick reproduction of bugs in textstats."""
from textstats import summarize

# Test 1: tabs and newlines should be treated as whitespace separators
print("Test 1 - whitespace handling:")
result = summarize("hello\tworld\nfoo")
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"
print(f"  PASS: {result}")

# Test 2: case-insensitive unique count with punctuation stripping
print("\nTest 2 - case/punctuation:")
result = summarize('Dog. says "dog," hello?')
assert result["words"] == 4, f"Expected 4 words, got {result['words']}"
assert result["unique"] == 3, f"Expected 3 unique (dog, says, hello), got {result['unique']}"
print(f"  PASS: {result}")

# Test 2b: Dog. and dog should be same word
print("\nTest 2b - case insensitive:")
result = summarize("Dog. dog DOG")
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"
assert result["unique"] == 1, f"Expected 1 unique (dog), got {result['unique']}"
print(f"  PASS: {result}")

# Test 3: empty input should not raise and return zeros
print("\nTest 3 - empty input:")
try:
    result = summarize("")
except Exception as e:
    print(f"  FAIL: raised {e}")
    exit(1)
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result}"
print(f"  PASS: {result}")

# Test 4: punctuation-only tokens should be ignored
print("\nTest 4 - punctuation only:")
result = summarize("... !!! ???")
assert result["words"] == 0, f"Expected 0 words, got {result['words']}"
print(f"  PASS: {result}")

# Test 5: multiple spaces between words
print("\nTest 5 - multiple spaces:")
result = summarize("hello   world")
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"
print(f"  PASS: {result}")

# Test 6: avg_len rounding (ab=2, cd=2, efgh=4 -> mean = 8/3 ≈ 2.67)
print("\nTest 6 - avg_len rounding:")
result = summarize("ab cd efgh")
assert result["avg_len"] == round(8/3, 2), f"Expected {round(8/3, 2)}, got {result['avg_len']}"
print(f"  PASS: {result}")

# Test 7: leading/trailing punctuation on words (4 tokens)
print("\nTest 7 - punctuation stripping:")
result = summarize("'Hello,' said the dog!")
assert result["words"] == 4, f"Expected 4 words, got {result['words']}"
assert result["unique"] == 4, f"Expected 4 unique, got {result['unique']}"
print(f"  PASS: {result}")

# Test 8: mixed whitespace
print("\nTest 8 - mixed whitespace:")
result = summarize("a\t\t\nb   c")
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"
print(f"  PASS: {result}")

# Test 9: avg_len with single word
print("\nTest 9 - single word:")
result = summarize("hello")
assert result["avg_len"] == 5.0, f"Expected 5.0, got {result['avg_len']}"
print(f"  PASS: {result}")

# Test 10: only whitespace input
print("\nTest 10 - only whitespace:")
result = summarize("   \t\n  ")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result}"
print(f"  PASS: {result}")

# Test 11: leading/trailing punctuation on same word
print("\nTest 11 - internal punctuation preserved:")
result = summarize("don't can't")
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"
print(f"  PASS: {result}")

# Test 12: avg_len with no words returns float 0.0
print("\nTest 12 - avg_len type for empty:")
result = summarize("")
assert isinstance(result["avg_len"], float), f"Expected float, got {type(result['avg_len'])}"
print(f"  PASS: {result}")

print("\nAll tests passed!")
