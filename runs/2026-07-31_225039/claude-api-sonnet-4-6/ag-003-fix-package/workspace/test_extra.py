from textstats import summarize

# Whitespace-only input
r = summarize("   \t\n  ")
assert r == {"words": 0, "unique": 0, "avg_len": 0.0}, f"whitespace-only: {r}"

# Mixed punctuation stripping
r = summarize('"Hello," she said.')
# tokens: '"Hello,"' -> 'hello', 'she' -> 'she', 'said.' -> 'said'
assert r["words"] == 3, f"words: {r}"
assert r["unique"] == 3, f"unique: {r}"
expected_avg = round((5 + 3 + 4) / 3, 2)
assert r["avg_len"] == expected_avg, f"avg_len: {r} expected {expected_avg}"

# Punctuation-only token
r = summarize("one ... two")
assert r["words"] == 2, f"punct-only words: {r}"
assert r["unique"] == 2, f"punct-only unique: {r}"

# Multiple spaces, tabs, newlines
r = summarize("a  b\tc\nd")
assert r["words"] == 4, f"multi-whitespace: {r}"

print("All extra tests passed!")
