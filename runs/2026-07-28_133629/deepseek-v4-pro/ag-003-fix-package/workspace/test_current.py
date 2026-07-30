from textstats import summarize

# Test 1: Empty input
print("Empty:", summarize(""))

# Test 2: Basic
print("Basic:", summarize("hello world"))

# Test 3: Multiple whitespace
print("Multi whitespace:", summarize("hello   world\ttab\nnewline"))

# Test 4: Case-insensitive
print("Case:", summarize("Dog dog DOG"))

# Test 5: Punctuation
print("Punct:", summarize("Hello, World! How's it going?"))

# Test 6: Only punctuation
print("Only punct:", summarize("!!! ... ???"))

# Test 7: Mixed
print("Mixed:", summarize("  Hello, ... world!  "))

# Test 8: Complex
print("Complex:", summarize("Dog. dog, \"dog\" 'dog' (dog) !!!"))

# Test 9: Single word with punctuation
print("Single:", summarize("  Hello!!!  "))
