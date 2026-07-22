"""Reproduce bugs in textstats.summarize."""
from textstats import summarize

# Test 1: Any whitespace (tabs, newlines)
print("Test 1 - any whitespace:")
result = summarize("hello\tworld\nfoo")
print(f"  words={result['words']} unique={result['unique']} avg_len={result['avg_len']}")
assert result["words"] == 3

# Test 2: Multiple consecutive whitespace
print("Test 2 - multiple spaces:")
result = summarize("hello   world")
print(f"  words={result['words']} unique={result['unique']} avg_len={result['avg_len']}")
assert result["words"] == 2

# Test 3: Case-insensitive unique count
print("Test 3 - case insensitive:")
result = summarize("Dog. dog DOG")
print(f"  words={result['words']} unique={result['unique']} avg_len={result['avg_len']}")
assert result["unique"] == 1

# Test 4: Punctuation stripping for uniqueness
print("Test 4 - punctuation:")
result = summarize('Dog. "dog" (dog)')
print(f"  words={result['words']} unique={result['unique']}")
assert result["unique"] == 1

# Test 5: Punctuation-only tokens don't count
print("Test 5 - punctuation only:")
result = summarize('... !!! ???')
print(f"  words={result['words']} unique={result['unique']} avg_len={result['avg_len']}")
assert result["words"] == 0

# Test 6: Empty input
print("Test 6 - empty:")
result = summarize("")
print(f"  words={result['words']} unique={result['unique']} avg_len={result['avg_len']}")
assert result["words"] == 0 and result["unique"] == 0 and result["avg_len"] == 0.0

# Test 7: avg_len rounding (2+2+3)/3 = 2.33
print("Test 7 - avg_len:")
result = summarize("ab cd efg")
print(f"  words={result['words']} unique={result['unique']} avg_len={result['avg_len']}")
assert result["avg_len"] == 2.33

# Test 8: Mixed punctuation and whitespace edge cases
print("Test 8 - mixed:")
result = summarize('  Hello, world!  ')
print(f"  words={result['words']} unique={result['unique']} avg_len={result['avg_len']}")
assert result["words"] == 2
assert result["unique"] == 2

# Test 9: Only whitespace
print("Test 9 - only whitespace:")
result = summarize("   \t\n  ")
print(f"  words={result['words']} unique={result['unique']} avg_len={result['avg_len']}")
assert result["words"] == 0 and result["unique"] == 0 and result["avg_len"] == 0.0

# Test 10: Leading/trailing whitespace with content
print("Test 10 - leading/trailing:")
result = summarize("   hello world   ")
print(f"  words={result['words']} unique={result['unique']} avg_len={result['avg_len']}")
assert result["words"] == 2

print("\nAll tests passed!")
