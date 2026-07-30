from textstats import summarize

# Test 1: Basic with mixed whitespace and punctuation
text = "Hello world! How are you? I'm fine."
print("Test 1:", summarize(text))

# Test 2: Case insensitivity
text2 = "Dog. dog DOG"
print("Test 2:", summarize(text2))

# Test 3: Only punctuation, no words
text3 = "!@#$%^&*"
print("Test 3:", summarize(text3))

# Test 4: Empty string
text4 = ""
print("Test 4:", summarize(text4))

# Test 5: Tabs and newlines
text5 = "word1\t\nword2   word3"
print("Test 5:", summarize(text5))
