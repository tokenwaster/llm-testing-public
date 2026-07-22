from textstats import summarize

# Test 1: Multiple whitespace types (tabs, newlines, multiple spaces)
text1 = "Hello\tworld\n  foo   bar"
result1 = summarize(text1)
print(f"Test 1 (whitespace): {result1}")
print(f"  Expected words=4, got words={result1['words']}")
assert result1['words'] == 4, f"Expected 4 words, got {result1['words']}"

# Test 2: Case-insensitive unique + punctuation stripping
text2 = "Dog. dog DOG cat,"
result2 = summarize(text2)
print(f"Test 2 (case/punct): {result2}")
print(f"  Expected words=4, unique=2, got words={result2['words']}, unique={result2['unique']}")
assert result2['words'] == 4
assert result2['unique'] == 2

# Test 3: Empty input
text3 = ""
result3 = summarize(text3)
print(f"Test 3 (empty): {result3}")
assert result3 == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result3}"

# Test 4: Punctuation-only tokens should not count
text4 = "... !!!"
result4 = summarize(text4)
print(f"Test 4 (punct only): {result4}")
assert result4 == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result4}"

# Test 5: avg_len calculation
text5 = "Hi there"
result5 = summarize(text5)
print(f"Test 5 (avg_len): {result5}")
# "hi"=2, "there"=5, avg=(2+5)/2=3.5
assert result5['avg_len'] == 3.5, f"Expected 3.5, got {result5['avg_len']}"

print("\nAll tests passed!")
