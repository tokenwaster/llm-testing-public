"""Reproduce the bugs before fixing."""
from textstats import summarize

# Bug 1: tokenize doesn't handle tabs/newlines/multiple spaces
text1 = "hello\tworld\nfoo   bar"
result1 = summarize(text1)
print(f"Multi-whitespace: {result1}")
assert result1["words"] == 4, f"Expected 4 words, got {result1['words']}"

# Bug 2: empty input should not raise
text2 = ""
try:
    result2 = summarize(text2)
    print(f"Empty input: {result2}")
except ZeroDivisionError:
    print("BUG: Empty input raised ZeroDivisionError")

# Bug 3: case-insensitive unique + punctuation stripping
text3 = 'Dog. dog DOG "cat" cat'
result3 = summarize(text3)
print(f"Punctuation/case test: {result3}")
assert result3["words"] == 5, f"Expected 5 words, got {result3['words']}"
assert result3["unique"] == 2, f"Expected 2 unique, got {result3['unique']}"

# Bug 4: token that is only punctuation should not count
text4 = '... !!! ???'
result4 = summarize(text4)
print(f"Punctuation-only tokens: {result4}")
assert result4["words"] == 0, f"Expected 0 words, got {result4['words']}"

# avg_len check
text5 = "hello world"
result5 = summarize(text5)
print(f"Avg len test: {result5}")
assert result5["avg_len"] == 5.0, f"Expected 5.0, got {result5['avg_len']}"

print("All tests passed!")
