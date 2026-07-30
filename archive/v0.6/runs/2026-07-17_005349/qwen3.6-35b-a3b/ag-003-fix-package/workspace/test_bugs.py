from textstats import summarize

# Test 1: Multiple whitespace (tabs, newlines, multiple spaces)
text1 = "hello\tworld\n  foo   bar"
result1 = summarize(text1)
print(f"Test 1 (whitespace): {result1}")
assert result1["words"] == 4, f"Expected 4 words, got {result1['words']}"

# Test 2: Case-insensitive unique
text2 = "Dog dog DOG cat"
result2 = summarize(text2)
print(f"Test 2 (case): {result2}")
assert result2["unique"] == 2, f"Expected 2 unique, got {result2['unique']}"

# Test 3: Punctuation stripping
text3 = "Hello, world! How's it going?"
result3 = summarize(text3)
print(f"Test 3 (punctuation): {result3}")
assert result3["words"] == 5, f"Expected 5 words, got {result3['words']}"

# Test 4: Empty input
text4 = ""
result4 = summarize(text4)
print(f"Test 4 (empty): {result4}")
assert result4 == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result4}"

# Test 5: Only punctuation
text5 = "... !!! ???"
result5 = summarize(text5)
print(f"Test 5 (punctuation only): {result5}")
assert result5 == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result5}"

# Test 6: avg_len calculation
text6 = "hi there"
result6 = summarize(text6)
print(f"Test 6 (avg_len): {result6}")
# "hi" = 2, "there" = 5, avg = 3.5
assert result6["avg_len"] == 3.5, f"Expected 3.5, got {result6['avg_len']}"

print("\nAll tests passed!")
