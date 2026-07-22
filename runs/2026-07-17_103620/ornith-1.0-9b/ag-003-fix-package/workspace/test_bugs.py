from textstats import summarize

# Test 1: Multiple whitespace (tabs, newlines)
r1 = summarize("Hello\tWorld\nFoo")
print(f"Test 1 - multiple whitespace: {r1}")
assert r1["words"] == 3, f"Expected words=3, got {r1['words']}"

# Test 2: Case-insensitive unique
r2 = summarize("Dog. dog DOG")
print(f"Test 2 - case insensitive: {r2}")
assert r2["unique"] == 1, f"Expected unique=1, got {r2['unique']}"

# Test 3: Only punctuation tokens don't count
r3 = summarize("... !!! ,,,")
print(f"Test 3 - only punctuation: {r3}")
assert r3["words"] == 0, f"Expected words=0, got {r3['words']}"
assert r3["unique"] == 0, f"Expected unique=0, got {r3['unique']}"

# Test 4: Empty input
r4 = summarize("")
print(f"Test 4 - empty input: {r4}")
assert r4 == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Got {r4}"

# Test 5: Punctuation stripped from words
r5 = summarize("Hello, world!")
print(f"Test 5 - punctuation stripped: {r5}")
assert r5["words"] == 2, f"Expected words=2, got {r5['words']}"
assert r5["unique"] == 2, f"Expected unique=2, got {r5['unique']}"

# Test 6: avg_len rounded to 2 decimals
r6 = summarize("abc def ghi")
print(f"Test 6 - avg_len: {r6}")
assert r6["avg_len"] == 3.0, f"Expected avg_len=3.0, got {r6['avg_len']}"

# Test 7: Mixed punctuation and whitespace
r7 = summarize("Hello   World\tFoo\nBar")
print(f"Test 7 - mixed whitespace: {r7}")
assert r7["words"] == 4, f"Expected words=4, got {r7['words']}"

# Test 8: Token that is only punctuation after cleaning should not count
r8 = summarize("Hello (World)")
print(f"Test 8 - parenthesized: {r8}")
assert r8["words"] == 2, f"Expected words=2, got {r8['words']}"

# Test 9: Multiple consecutive spaces and tabs
r9 = summarize("A\t\tB   C")
print(f"Test 9 - multiple whitespace chars: {r9}")
assert r9["words"] == 3, f"Expected words=3, got {r9['words']}"

print("\nAll tests passed!")
