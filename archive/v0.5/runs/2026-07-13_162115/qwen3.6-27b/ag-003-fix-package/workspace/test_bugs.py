from textstats import summarize

# Test 1: Multiple spaces and tabs
print("Test 1 - multiple whitespace:")
result = summarize("hello   world\t\ttest")
print(f"  Result: {result}")
print(f"  Expected words=3, got words={result['words']}")

# Test 2: Case-insensitive unique
print("\nTest 2 - case insensitive:")
result = summarize("Dog dog DOG")
print(f"  Result: {result}")
print(f"  Expected unique=1, got unique={result['unique']}")

# Test 3: Punctuation stripping
print("\nTest 3 - punctuation:")
result = summarize("Hello, world!")
print(f"  Result: {result}")
print(f"  Expected unique=2, got unique={result['unique']}")

# Test 4: Only punctuation tokens
print("\nTest 4 - only punctuation:")
result = summarize("... !!! ???")
print(f"  Result: {result}")
print(f"  Expected words=0, got words={result['words']}")

# Test 5: Empty input
print("\nTest 5 - empty input:")
try:
    result = summarize("")
    print(f"  Result: {result}")
    print(f"  Expected words=0, unique=0, avg_len=0.0")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

# Test 6: Newlines
print("\nTest 6 - newlines:")
result = summarize("hello\nworld\ntest")
print(f"  Result: {result}")
print(f"  Expected words=3, got words={result['words']}")

# Test 7: avg_len calculation
print("\nTest 7 - avg_len:")
result = summarize("hi there")
print(f"  Result: {result}")
print(f"  Expected avg_len=3.0, got avg_len={result['avg_len']}")
