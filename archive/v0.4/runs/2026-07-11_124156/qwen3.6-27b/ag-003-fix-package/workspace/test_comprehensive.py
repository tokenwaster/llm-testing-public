from textstats import summarize

# Test 1: Basic functionality
r = summarize("hello world")
assert r == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Test 1 failed: {r}"

# Test 2: Multiple whitespace
r = summarize("hello   world\t\nfoo")
assert r == {"words": 3, "unique": 3, "avg_len": 4.33}, f"Test 2 failed: {r}"

# Test 3: Case-insensitive unique
r = summarize("Dog dog DOG")
assert r == {"words": 3, "unique": 1, "avg_len": 3.0}, f"Test 3 failed: {r}"

# Test 4: Empty input
r = summarize("")
assert r == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Test 4 failed: {r}"

# Test 5: Only punctuation
r = summarize("... !!! ???")
assert r == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Test 5 failed: {r}"

# Test 6: Punctuation stripping
r = summarize('Hello, world! "Test"')
assert r == {"words": 3, "unique": 3, "avg_len": 4.67}, f"Test 6 failed: {r}"

# Test 7: Mixed punctuation and case
r = summarize('The the THE, the!')
assert r == {"words": 4, "unique": 1, "avg_len": 3.0}, f"Test 7 failed: {r}"

# Test 8: Only whitespace
r = summarize("   \t\n  ")
assert r == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Test 8 failed: {r}"

# Test 9: Single word
r = summarize("hello")
assert r == {"words": 1, "unique": 1, "avg_len": 5.0}, f"Test 9 failed: {r}"

# Test 10: All same word with different punctuation
r = summarize("'hello' \"hello\" (hello)")
assert r == {"words": 3, "unique": 1, "avg_len": 5.0}, f"Test 10 failed: {r}"

print("All tests passed!")
