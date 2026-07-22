from textstats import summarize

# Additional edge case tests
print("Test: Tabs and newlines")
result = summarize("hello\tworld\nfoo")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 3, 'unique': 3, 'avg_len': 4.33}}")

print("\nTest: Multiple spaces")
result = summarize("hello    world")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")

print("\nTest: Punctuation in middle (should not be stripped)")
result = summarize("can't won't")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")

print("\nTest: Mixed case with punctuation")
result = summarize("Hello! HELLO? hello.")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 3, 'unique': 1, 'avg_len': 5.0}}")

print("\nTest: Only punctuation tokens mixed")
result = summarize("word ... another !!!")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.5}}")

print("\nTest: Single character words")
result = summarize("a b c")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 3, 'unique': 3, 'avg_len': 1.0}}")

print("\nTest: Unicode (should work with split)")
result = summarize("café naïve")
print(f"  Result: {result}")
print(f"  Expected: {{'words': 2, 'unique': 2, 'avg_len': 5.0}}")