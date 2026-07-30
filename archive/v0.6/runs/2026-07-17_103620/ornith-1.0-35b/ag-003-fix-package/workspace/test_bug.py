"""Reproduce bugs before fixing."""
from textstats import summarize

# Test 1: whitespace handling (tabs, newlines)
print("Test 1 - whitespace:")
result = summarize("hello\tworld\nfoo")
print(result)
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"

# Test 2: case-insensitive unique with punctuation stripping
print("\nTest 2 - case/punctuation:")
result = summarize('Dog. says "dog"!')
print(result)
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"
# Dog and dog are same; says is different -> 2 unique
assert result["unique"] == 2, f"Expected 2 unique, got {result['unique']}"

# Test 3: token that is only punctuation should not count as a word
print("\nTest 3 - pure punctuation token:")
result = summarize("hello ... world")
print(result)
assert result["words"] == 2, f"Expected 2 words, got {result['words']}"

# Test 4: empty input must not raise
print("\nTest 4 - empty input:")
try:
    result = summarize("")
    print(result)
    assert result == {"words": 0, "unique": 0, "avg_len": 0.0}
except Exception as e:
    print(f"FAILED with {e}")

# Test 5: only punctuation input
print("\nTest 5 - only punctuation:")
try:
    result = summarize("... !!!")
    print(result)
    assert result == {"words": 0, "unique": 0, "avg_len": 0.0}
except Exception as e:
    print(f"FAILED with {e}")

# Test 6: avg_len rounding
print("\nTest 6 - avg_len:")
result = summarize("ab cd ef")
print(result)
assert result["avg_len"] == 2.0, f"Expected 2.0, got {result['avg_len']}"

# Test 7: multiple spaces between words
print("\nTest 7 - multiple spaces:")
result = summarize("a   b    c")
print(result)
assert result["words"] == 3, f"Expected 3 words, got {result['words']}"
