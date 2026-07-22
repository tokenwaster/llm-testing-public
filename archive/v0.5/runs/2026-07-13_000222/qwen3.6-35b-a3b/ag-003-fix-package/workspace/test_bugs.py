from textstats import summarize

# Test 1: Empty input should not raise
print("Test 1: Empty input")
try:
    result = summarize("")
    print(f"  Result: {result}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

# Test 2: Tabs and newlines should be treated as word separators
print("\nTest 2: Tabs and newlines")
result = summarize("hello\tworld\nfoo")
print(f"  Result: {result}")
print(f"  Expected: words=3, unique=3, avg_len=5.0")

# Test 3: Multiple spaces
print("\nTest 3: Multiple spaces")
result = summarize("hello   world")
print(f"  Result: {result}")
print(f"  Expected: words=2, unique=2, avg_len=5.0")

# Test 4: Punctuation stripping and case-insensitivity
print("\nTest 4: Punctuation and case")
result = summarize("Dog. cat, DOG")
print(f"  Result: {result}")
print(f"  Expected: words=3, unique=2, avg_len=3.67")

# Test 5: Punctuation-only tokens should not count
print("\nTest 5: Punctuation-only tokens")
result = summarize("... ,,, !!!")
print(f"  Result: {result}")
print(f"  Expected: words=0, unique=0, avg_len=0.0")

# Test 6: Mixed whitespace
print("\nTest 6: Mixed whitespace")
result = summarize("  hello\t\tworld\n\nfoo  ")
print(f"  Result: {result}")
print(f"  Expected: words=3, unique=3, avg_len=5.0")
