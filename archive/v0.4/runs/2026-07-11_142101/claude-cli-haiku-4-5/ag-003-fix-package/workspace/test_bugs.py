"""Test script to reproduce textstats bugs."""
from textstats import summarize

# Test 1: Empty input should return 0 for all fields without raising
print("Test 1: Empty input")
try:
    result = summarize("")
    print(f"  Result: {result}")
    assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected empty result, got {result}"
    print("  PASS")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 2: Only punctuation should be handled properly
print("\nTest 2: Only punctuation")
try:
    result = summarize(".,;:!?\"'()")
    print(f"  Result: {result}")
    assert result == {"words": 0, "unique": 0, "avg_len": 0.0}, f"Expected empty result, got {result}"
    print("  PASS")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 3: Case insensitivity for unique words
print("\nTest 3: Case insensitivity")
try:
    result = summarize("Dog dog DOG")
    print(f"  Result: {result}")
    # 3 total words, 1 unique word (case-insensitive), avg_len = 3.0
    assert result["words"] == 3, f"Expected 3 words, got {result['words']}"
    assert result["unique"] == 1, f"Expected 1 unique word, got {result['unique']}"
    assert result["avg_len"] == 3.0, f"Expected avg_len 3.0, got {result['avg_len']}"
    print("  PASS")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 4: Punctuation stripped for unique and avg_len
print("\nTest 4: Punctuation stripping")
try:
    result = summarize("Dog. dog")
    print(f"  Result: {result}")
    # 2 total words, 1 unique word (case-insensitive, punctuation stripped), avg_len = 3.0
    assert result["words"] == 2, f"Expected 2 words, got {result['words']}"
    assert result["unique"] == 1, f"Expected 1 unique word, got {result['unique']}"
    assert result["avg_len"] == 3.0, f"Expected avg_len 3.0, got {result['avg_len']}"
    print("  PASS")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 5: Any whitespace separation (tabs, newlines, multiple spaces)
print("\nTest 5: Any whitespace separation")
try:
    result = summarize("hello  world\ttest\nfoo")
    print(f"  Result: {result}")
    # 4 words (hello, world, test, foo) + 1 empty from double space, separated by tab, newline
    # Actually, need to see what split() does with multiple spaces
    # "hello  world" with split(" ") gives ["hello", "", "world"]
    # We should be using split() with no args or split whitespace
    print(f"  Actual tokens: {summarize.__doc__}")
except Exception as e:
    print(f"  ✗ FAIL: {e}")

# Test 6: Basic case
print("\nTest 6: Basic case")
try:
    result = summarize("hello world test")
    print(f"  Result: {result}")
    # 3 words, 3 unique, avg_len = (5+5+4)/3 = 4.67
    assert result["words"] == 3, f"Expected 3 words, got {result['words']}"
    assert result["unique"] == 3, f"Expected 3 unique words, got {result['unique']}"
    assert result["avg_len"] == round((5+5+4)/3, 2), f"Expected avg_len {round((5+5+4)/3, 2)}, got {result['avg_len']}"
    print("  PASS")
except Exception as e:
    print(f"  FAIL: {e}")
