from textstats import summarize

# Test 1: whitespace splitting (tabs, newlines, multiple spaces)
text1 = "hello\tworld\nfoo  bar"
result1 = summarize(text1)
print(f"Test 1 (whitespace): {result1}")
assert result1["words"] == 4, f"Expected 4 words, got {result1['words']}"

# Test 2: punctuation stripping, case-insensitive
text2 = "Dog. dog DOG"
result2 = summarize(text2)
print(f"Test 2 (punctuation/case): {result2}")
assert result2["words"] == 3, f"Expected 3 words, got {result2['words']}"
assert result2["unique"] == 1, f"Expected 1 unique, got {result2['unique']}"

# Test 3: empty input
text3 = ""
result3 = summarize(text3)
print(f"Test 3 (empty): {result3}")
assert result3 == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {result3}"

# Test 4: punctuation-only tokens should not count
text4 = "... !!!"
result4 = summarize(text4)
print(f"Test 4 (punct only): {result4}")
assert result4["words"] == 0, f"Expected 0 words, got {result4['words']}"

# Test 5: avg_len calculation
text5 = "hi there"
result5 = summarize(text5)
print(f"Test 5 (avg_len): {result5}")
assert result5["avg_len"] == 3.5, f"Expected 3.5, got {result5['avg_len']}"

print("All tests passed!")
