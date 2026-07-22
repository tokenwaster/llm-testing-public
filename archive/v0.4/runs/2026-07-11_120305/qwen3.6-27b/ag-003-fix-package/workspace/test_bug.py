from textstats import summarize

# Test 1: basic case
print("Test 1:", summarize("hello world"))

# Test 2: case insensitive
print("Test 2:", summarize("Dog dog DOG"))

# Test 3: punctuation stripping
print("Test 3:", summarize("Dog. dog"))

# Test 4: multiple whitespace
print("Test 4:", summarize("hello   world\t\nfoo"))

# Test 5: empty input
print("Test 5:", summarize(""))

# Test 6: only punctuation
print("Test 6:", summarize("... !!!"))

# Test 7: punctuation-only tokens
print("Test 7:", summarize("hello ... world"))
