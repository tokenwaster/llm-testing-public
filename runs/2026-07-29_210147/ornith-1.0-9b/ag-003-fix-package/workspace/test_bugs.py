from textstats import summarize

# Bug 1: tokenize uses split(" ") instead of any whitespace
print("Test 1 (tabs/newlines):", summarize("hello\tworld\nfoo"))
assert summarize("hello\tworld\nfoo") == {"words":3,"unique":3,"avg_len":4.33}, "FAIL"

# Bug 2: No case-insensitive unique count
print("Test 2 (case insensitive):", summarize("Dog. dog"))
result = summarize("Dog. dog")
assert result["unique"] == 1, f"FAIL: got {result}"

# Bug 3: Division by zero on empty input
try:
    print("Test 3 (empty input):", summarize(""))
except Exception as e:
    print(f"Test 3 FAILED with: {e}")
assert summarize("") == {"words":0,"unique":0,"avg_len":0.0}, "FAIL empty"

# Test only-punctuation token doesn't count
print("Test 4 (only punctuation):", summarize("..."))
result = summarize("...")
assert result["words"] == 0 and result["unique"] == 0, f"FAIL: got {result}"

# Additional edge cases
print("Test 5 (multiple whitespace):", summarize("  hello   world  "))
assert summarize("  hello   world  ") == {"words":2,"unique":2,"avg_len":4.5}, "FAIL multi-whitespace"

print("Test 6 (punctuation stripped):", summarize('"Hello, World!"'))
result = summarize('"Hello, World!"')
# Cleaned: 'hello', 'world' -> lengths 5, 5 -> avg 5.0
assert result["words"] == 2 and result["unique"] == 2 and result["avg_len"] == 5.0, f"FAIL: got {result}"

print("Test 7 (single word):", summarize("hello"))
assert summarize("hello") == {"words":1,"unique":1,"avg_len":5.0}, "FAIL single"

# Test that punctuation-only tokens don't count as words
print("Test 8 (mixed punct and real words):", summarize('"..." hello'))
result = summarize('"..." hello')
assert result["words"] == 2, f"FAIL: got {result}"
assert result["unique"] == 1, f"FAIL unique: got {result}"

# Test with only whitespace
print("Test 9 (only whitespace):", summarize("   \t\n  "))
assert summarize("   \t\n  ") == {"words":0,"unique":0,"avg_len":0.0}, "FAIL whitespace-only"

# Test avg_len rounding to 2 decimals
result = summarize("abc def")
print(f"Test 10 (rounding): {result}")
assert result["avg_len"] == 4.5, f"FAIL: got {result}"

print("\nAll tests passed!")
