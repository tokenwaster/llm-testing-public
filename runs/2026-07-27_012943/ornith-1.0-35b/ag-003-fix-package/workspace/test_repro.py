from textstats import summarize

# Test 1: Basic case with mixed whitespace (tabs, newlines)
result = summarize("hello\tworld\nfoo")
print(f"Test 1 - mixed whitespace: {result}")
assert result == {"words": 3, "unique": 3, "avg_len": 4.33}, f"FAIL: got {result}"

# Test 2: Punctuation handling - case insensitive
result = summarize('Dog. dog DOG!')
print(f"Test 2 - case/punct: {result}")
assert result == {"words": 3, "unique": 1, "avg_len": 3.0}, f"FAIL: got {result}"

# Test 3: Empty input
result = summarize("")
print(f"Test 3 - empty: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"FAIL: got {result}"

# Test 4: Only punctuation (should not count as words)
result = summarize("... !!! ???")
print(f"Test 4 - only punct: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"FAIL: got {result}"

# Test 5: Multiple spaces between words (shouldn't produce empty tokens)
result = summarize("hello   world")
print(f"Test 5 - multiple spaces: {result}")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"FAIL: got {result}"

# Test 6: Leading/trailing punctuation on words (length unaffected by case)
result = summarize('"Hello," said the dog.')
print(f"Test 6 - mixed punct: {result}")
assert result == {"words": 4, "unique": 4, "avg_len": 3.75}, f"FAIL: got {result}"

# Test 7: Only whitespace
result = summarize("   \t\n  ")
print(f"Test 7 - only whitespace: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"FAIL: got {result}"

# Test 8: Words with surrounding punctuation (quotes)
result = summarize("'Hello' 'World'")
print(f"Test 8 - quotes: {result}")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"FAIL: got {result}"

# Test 9: Parentheses around a word
result = summarize("(hello)")
print(f"Test 9 - parens: {result}")
assert result == {"words": 1, "unique": 1, "avg_len": 5.0}, f"FAIL: got {result}"

# Test 10: Mixed case-insensitive with punctuation
result = summarize("cat Cat CAT.")
print(f"Test 10 - case insensitive: {result}")
assert result == {"words": 3, "unique": 1, "avg_len": 3.0}, f"FAIL: got {result}"

# Test 11: Tab-separated words
result = summarize("a\tb\tc")
print(f"Test 11 - tabs: {result}")
assert result == {"words": 3, "unique": 3, "avg_len": 1.0}, f"FAIL: got {result}"

# Test 12: Single char word
result = summarize("a")
print(f"Test 12 - single char: {result}")
assert result == {"words": 1, "unique": 1, "avg_len": 1.0}, f"FAIL: got {result}"

# Test 13: avg_len rounding to 2 decimals with non-integer average
result = summarize("ab cd ef gh ij")
print(f"Test 13 - rounding: {result}")
assert result["avg_len"] == 2.0, f"FAIL: got {result}"

# Test 14: avg_len rounding actual non-trivial case
result = summarize("a bb ccc dddd eeeee")
print(f"Test 14 - rounding nontrivial: {result}")
assert result["avg_len"] == 3.0, f"FAIL: got {result}"

# Test 15: avg_len with actual rounding needed
result = summarize("a bb ccc dddd")
print(f"Test 15 - rounding needed: {result}")
expected_avg = round(10/4, 2)  # 2.5
assert result["avg_len"] == expected_avg, f"FAIL: got {result}"

# Test 16: Punctuation-only tokens should not count in words or unique
result = summarize("... dog ...")
print(f"Test 16 - punct only between words: {result}")
assert result == {"words": 1, "unique": 1, "avg_len": 3.0}, f"FAIL: got {result}"

# Test 17: Newlines in input
result = summarize("hello\nworld")
print(f"Test 17 - newlines: {result}")
assert result == {"words": 2, "unique": 2, "avg_len": 5.0}, f"FAIL: got {result}"

# Test 18: Tabs and mixed with punctuation
result = summarize("Hello,\tWorld!\nfoo.")
print(f"Test 18 - complex: {result}")
assert result == {"words": 3, "unique": 3, "avg_len": 5.0}, f"FAIL: got {result}"

# Test 19: avg_len rounding to exactly 2 decimals (e.g., 1/3 = 0.33)
result = summarize("a b c")
print(f"Test 19 - rounding 1/3: {result}")
assert result["avg_len"] == round(1.0, 2), f"FAIL: got {result}"

# Test 20: Mixed case with punctuation should still get correct avg_len
# "Dog." -> "dog" (len 3), "dog" -> "dog" (len 3) => avg = 3.0
result = summarize("Dog. dog")
print(f"Test 20 - case+punct avg: {result}")
assert result == {"words": 2, "unique": 1, "avg_len": 3.0}, f"FAIL: got {result}"

# Test 21: Whitespace-only with some punctuation tokens that become empty after strip
result = summarize("... ...")
print(f"Test 21 - all punct tokens: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"FAIL: got {result}"

# Test 22: Punctuation at edges only
result = summarize("...")
print(f"Test 22 - single punct token: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"FAIL: got {result}"

# Test 23: Mixed tabs and spaces
result = summarize("a b\tc   d\te")
print(f"Test 23 - mixed separators: {result}")
assert result == {"words": 5, "unique": 5, "avg_len": 1.0}, f"FAIL: got {result}"

# Test 24: Verify no function signature changes
import inspect
from textstats.helpers import tokenize, clean
sig_t = inspect.signature(tokenize)
sig_c = inspect.signature(clean)
print(f"Test 24 - signatures: tokenize{sig_t}, clean{sig_c}")
assert len(sig_t.parameters) == 1, f"tokenize signature changed"
assert len(sig_c.parameters) == 1, f"clean signature changed"

# Test 25: Punctuation inside word is preserved (only leading/trailing stripped)
result = summarize("don't can't")
print(f"Test 25 - internal apostrophe: {result}")
assert result["words"] == 2 and result["unique"] == 2, f"FAIL: got {result}"

print("\nAll tests passed!")
