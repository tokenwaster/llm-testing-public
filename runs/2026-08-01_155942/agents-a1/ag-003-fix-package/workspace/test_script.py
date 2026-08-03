from textstats import summarize

# Test 1: basic case with punctuation and newlines, mixed case, duplicate words after normalization
text = "Hello, world! This is a test. Hello again."
result = summarize(text)
print("Test 1:", result)
words_expected = ["hello", "world", "this", "is", "a", "test", "hello", "again"]
# After cleaning: same tokens lowercased; note 'Hello' appears twice (first and seventh).
expected_words = len(words_expected)
print(f"  words={result['words']}, unique={result['unique']}")

# Test 2: only punctuation tokens (should return zero - all stripped to empty or non-letters?)
text = "! ? ..."
result = summarize(text)
print("Test 2:", result)
assert result == {"words":0, "unique":0, "avg_len":0.0}, f"Expected zeros but got {result}"

# Test 3: empty input
text = ""
result = summarize(text)
print("Test 3:", result)
assert result == {"words":0, "unique":0, "avg_len":0.0}

# Test 4: case insensitivity - "Dog" and "dog" should be same word
text = "Dog DOG dog."
result = summarize(text)
print("Test 4:", result)
assert result == {"words":3, "unique":1, "avg_len":3.0}, f"Unexpected {result}"

# Test 5: tabs and newlines as separators (split on any whitespace)
text = "Hello\tworld\nThis   is\tdown"
result = summarize(text)
print("Test 5:", result)
assert result["words"] == 5, f"Expected words=5 got {result['words']}"

# Test 6: leading/trailing punctuation stripped, token "-" (hyphen not in PUNCT list) should count as word because it's not only punctuation from the defined set? Spec says only those chars are considered for stripping.
text = "'Hello' - world"
result = summarize(text)
print("Test 6:", result)
# tokens: 'Hello', '-', world -> cleaned: hello, -, world => words=3 unique=3 avg_len=(5+1+5)/3 ≈ 3.67
assert result["words"] == 3 and result["unique"] == 3

# Test 7: token that is only punctuation from the defined set should be excluded entirely (e.g., ".", ",", "!")
text = "Hello . world , !"
result = summarize(text)
print("Test 7:", result)
assert result["words"] == 2, f"Expected words=2 got {result['words']}"

# Test 8: mixed punctuation and letters like "(abc)" should become 'abc'
text = "(abc) def (ghi)!"
result = summarize(text)
print("Test 8:", result)
assert result["words"] == 3, f"Expected words=3 got {result['words']}"

# Test 9: avg_len rounding to 2 decimals for non-integer values
text = "ab cd ef"
result = summarize(text)
print("Test 9:", result)
expected_avg = round((2+2+2)/3, 2) # 2.0 exactly? Actually all length=2 -> avg=2.0

# Test 10: single word with punctuation "Hello,"
text = "Hello,"
result = summarize(text)
print("Test 10:", result)
assert result["words"] == 1 and result["unique"] == 1 and result["avg_len"] == 5.0

print("\nAll tests passed!")
