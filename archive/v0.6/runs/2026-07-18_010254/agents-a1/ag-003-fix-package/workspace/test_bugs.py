from textstats import summarize

# Test 1: Multiple whitespace types (tabs, newlines)
print("Test 1:", summarize("Hello\tworld\nfoo"))

# Test 2: Case insensitivity
print("Test 2:", summarize("Dog. dog DOG"))

# Test 3: Punctuation-only tokens
print("Test 3:", summarize("... ... ,,, "))

# Test 4: Empty input
print("Test 4:", summarize(""))

# Test 5: Mixed punctuation and words
print("Test 5:", summarize("Hello, world! How are you?"))
