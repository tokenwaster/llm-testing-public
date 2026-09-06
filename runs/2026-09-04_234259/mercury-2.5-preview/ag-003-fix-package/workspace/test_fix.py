from textstats import summarize

# Test 1: Basic functionality
print("Test 1 - Basic:", summarize("Hello world"))

# Test 2: Multiple spaces/tabs/newlines
print("Test 2 - Whitespace:", summarize("Hello  world\n\ttest"))

# Test 3: Punctuation handling
print("Test 3 - Punctuation:", summarize("Dog. dog"))

# Test 4: Only punctuation
print("Test 4 - Only punctuation:", summarize("... !!!"))

# Test 5: Empty input
print("Test 5 - Empty:", summarize(""))

# Test 6: Mixed case uniqueness
print("Test 6 - Case insensitive:", summarize("Hello HELLO hello"))
