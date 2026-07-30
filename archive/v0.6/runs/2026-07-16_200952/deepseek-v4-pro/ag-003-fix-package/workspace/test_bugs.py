"""Quick test to find bugs in textstats."""
from textstats import summarize

# Test 1: Basic whitespace handling
print("Test 1 - whitespace:")
result = summarize("hello  world\ttest\nnew")
print(result)
# Expected: words=4, unique=4, avg_len=...

# Test 2: Case-insensitive unique
print("\nTest 2 - case-insensitive:")
result = summarize("Dog. dog DOG")
print(result)
# Expected: words=3, unique=1

# Test 3: Punctuation-only tokens
print("\nTest 3 - punctuation only:")
result = summarize("hello ... world")
print(result)
# Expected: words=2, unique=2 (the "..." should not count)

# Test 4: Empty input
print("\nTest 4 - empty:")
result = summarize("")
print(result)
# Expected: {"words": 0, "unique": 0, "avg_len": 0.0}

# Test 5: Leading/trailing punctuation
print("\nTest 5 - punctuation stripping:")
result = summarize('"Hello," she said.')
print(result)
# Expected: words=3, unique=3, avg_len=...

# Test 6: Only whitespace
print("\nTest 6 - only whitespace:")
result = summarize("   \t\n  ")
print(result)
# Expected: {"words": 0, "unique": 0, "avg_len": 0.0}