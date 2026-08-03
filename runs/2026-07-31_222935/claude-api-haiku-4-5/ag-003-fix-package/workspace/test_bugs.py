from textstats import summarize

# Test 1: Basic functionality
print("Test 1: Basic text")
result = summarize("Hello world")
print(f"Result: {result}")
print(f"Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.5}}")
print()

# Test 2: Case insensitivity
print("Test 2: Case insensitivity")
result = summarize("Dog dog DOG")
print(f"Result: {result}")
print(f"Expected: {{'words': 3, 'unique': 1, 'avg_len': 3.0}}")
print()

# Test 3: Punctuation handling
print("Test 3: Punctuation handling")
result = summarize("Dog. dog")
print(f"Result: {result}")
print(f"Expected: {{'words': 2, 'unique': 1, 'avg_len': 3.0}}")
print()

# Test 4: Multiple whitespace types
print("Test 4: Multiple whitespace types")
result = summarize("Hello\tworld\ntest")
print(f"Result: {result}")
print(f"Expected: {{'words': 3, 'unique': 3, 'avg_len': 4.67}}")
print()

# Test 5: Multiple spaces in a row
print("Test 5: Multiple spaces in a row")
result = summarize("Hello  world   test")
print(f"Result: {result}")
print(f"Expected: {{'words': 3, 'unique': 3, 'avg_len': 4.67}}")
print()

# Test 6: Tokens that are only punctuation
print("Test 6: Tokens that are only punctuation")
result = summarize("Hello ... world")
print(f"Result: {result}")
print(f"Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.5}}")
print()

# Test 7: Empty input
print("Test 7: Empty input")
result = summarize("")
print(f"Result: {result}")
print(f"Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
print()

# Test 8: Only whitespace
print("Test 8: Only whitespace")
result = summarize("   \t\n  ")
print(f"Result: {result}")
print(f"Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
print()

# Test 9: Only punctuation
print("Test 9: Only punctuation")
result = summarize("...,,,")
print(f"Result: {result}")
print(f"Expected: {{'words': 0, 'unique': 0, 'avg_len': 0.0}}")
