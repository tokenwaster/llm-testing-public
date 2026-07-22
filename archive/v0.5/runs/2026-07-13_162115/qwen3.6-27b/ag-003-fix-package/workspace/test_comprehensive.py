from textstats import summarize

# Test: Dog. and dog should be same word
r = summarize("Dog. dog")
assert r == {"words": 2, "unique": 1, "avg_len": 3.0}, f"Failed: {r}"

# Test: punctuation-only tokens excluded
r = summarize("Hello ... world !!!")
assert r == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Failed: {r}"

# Test: empty string
r = summarize("")
assert r == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Failed: {r}"

# Test: only whitespace
r = summarize("   \t\n  ")
assert r == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Failed: {r}"

# Test: mixed whitespace
r = summarize("a\tb\nc")
assert r == {"words": 3, "unique": 3, "avg_len": 1.0}, f"Failed: {r}"

# Test: avg_len rounding
r = summarize("hi hello hey")
# lengths: 2, 5, 3 => avg = 10/3 = 3.333... => 3.33
assert r == {"words": 3, "unique": 3, "avg_len": 3.33}, f"Failed: {r}"

# Test: punctuation on both sides
r = summarize("'Hello' \"world\"")
assert r == {"words": 2, "unique": 2, "avg_len": 5.0}, f"Failed: {r}"

# Test: single word
r = summarize("hello")
assert r == {"words": 1, "unique": 1, "avg_len": 5.0}, f"Failed: {r}"

# Test: all same word different cases
r = summarize("The THE the")
assert r == {"words": 3, "unique": 1, "avg_len": 3.0}, f"Failed: {r}"

print("All tests passed!")
