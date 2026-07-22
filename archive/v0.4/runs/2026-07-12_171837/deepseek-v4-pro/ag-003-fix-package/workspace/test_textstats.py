"""Quick test script to reproduce failures."""

from textstats import summarize

# Test 1: Basic
print("Test 1 - Basic:", summarize("Hello, world!"))

# Test 2: Case-insensitive unique
print("Test 2 - Case insensitive:", summarize("Dog. dog"))

# Test 3: Empty input
print("Test 3 - Empty:", summarize(""))

# Test 4: Only whitespace
print("Test 4 - Whitespace:", summarize("   "))

# Test 5: Tabs and newlines
print("Test 5 - Tabs/newlines:", summarize("a\tb\nc"))

# Test 6: Punctuation-only token
print("Test 6 - Punct only:", summarize("hello ... world"))

# Test 7: Multiple spaces
print("Test 7 - Multiple spaces:", summarize("hello    world"))