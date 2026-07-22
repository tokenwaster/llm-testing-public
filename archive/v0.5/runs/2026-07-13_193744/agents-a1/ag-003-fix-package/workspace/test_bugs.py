from textstats import summarize

# Test 1: Multiple whitespace types (tabs, newlines, multiple spaces)
text1 = "Hello\tworld\n   test"
print("Test 1:", summarize(text1))
# Expected: words=3, unique=3, avg_len=4.67

# Test 2: Case-insensitivity and punctuation stripping
text2 = "Dog. dog DOG!"
print("Test 2:", summarize(text2))
# Expected: words=3, unique=1, avg_len=3.0

# Test 3: Token that is only punctuation (should be ignored)
text3 = "... !!! ,,,"
print("Test 3:", summarize(text3))
# Expected: words=0, unique=0, avg_len=0.0

# Test 4: Mixed content with leading/trailing punctuation
text4 = "   'Hello,' world!   "
print("Test 4:", summarize(text4))
# Expected: words=2, unique=2, avg_len=5.0

# Test 5: Empty input
text5 = ""
print("Test 5:", summarize(text5))
# Expected: words=0, unique=0, avg_len=0.0
