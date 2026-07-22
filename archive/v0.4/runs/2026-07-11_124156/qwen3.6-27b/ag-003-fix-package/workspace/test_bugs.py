from textstats import summarize

# Test 1: Multiple whitespace / tabs / newlines
print("Test 1 - whitespace splitting:")
result = summarize("hello   world\t\nfoo")
print(f"  Result: {result}")
print(f"  Expected words=3, got words={result['words']}")

# Test 2: Case-insensitive uniqueness
print("\nTest 2 - case-insensitive unique:")
result = summarize("Dog dog DOG")
print(f"  Result: {result}")
print(f"  Expected unique=1, got unique={result['unique']}")

# Test 3: Empty input
print("\nTest 3 - empty input:")
try:
    result = summarize("")
    print(f"  Result: {result}")
    print(f"  Expected avg_len=0.0, got avg_len={result['avg_len']}")
except ZeroDivisionError as e:
    print(f"  ZeroDivisionError: {e}")

# Test 4: Only punctuation
print("\nTest 4 - only punctuation:")
try:
    result = summarize("... !!! ???")
    print(f"  Result: {result}")
    print(f"  Expected words=0, got words={result['words']}")
except ZeroDivisionError as e:
    print(f"  ZeroDivisionError: {e}")

# Test 5: Punctuation stripping
print("\nTest 5 - punctuation stripping:")
result = summarize('Hello, world! "Test"')
print(f"  Result: {result}")
print(f"  Expected words=3, unique=3, avg_len=4.33")
