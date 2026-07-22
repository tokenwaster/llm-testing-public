from textstats import summarize

# Test 1: Multiple whitespace types (tabs, newlines, multiple spaces)
result = summarize("hello  world\tfoo\nbar")
print(f"Test 1 (whitespace): {result}")
# Expected: words=4, unique=4, avg_len=4.25

# Test 2: Case-insensitive unique count
result = summarize("Dog. dog DOG")
print(f"Test 2 (case): {result}")
# Expected: words=3, unique=1, avg_len=3.0

# Test 3: Punctuation stripping
result = summarize("Hello, world! How are you?")
print(f"Test 3 (punctuation): {result}")
# Expected: words=5, unique=5, avg_len=4.2

# Test 4: Empty input
result = summarize("")
print(f"Test 4 (empty): {result}")
# Expected: words=0, unique=0, avg_len=0.0

# Test 5: Only punctuation
result = summarize("... !!! ???")
print(f"Test 5 (punct only): {result}")
# Expected: words=0, unique=0, avg_len=0.0

# Test 6: Tabs and newlines
result = summarize("a\tb\nc")
print(f"Test 6 (tabs/newlines): {result}")
# Expected: words=3, unique=3, avg_len=1.0

# Test 7: Leading/trailing punctuation
result = summarize("'Hello' \"World\"")
print(f"Test 7 (quotes): {result}")
# Expected: words=2, unique=2, avg_len=5.0
