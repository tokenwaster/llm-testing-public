from textstats import summarize

# Bug 1: tokenize uses split(" ") instead of split() — fails on tabs, newlines, multiple spaces
print("Test tabs/newlines/multi-space:")
try:
    r = summarize("hello\tworld\n foo")
    print(f"  Result: {r}")  # Expected: words=3
except Exception as e:
    print(f"  ERROR: {e}")

# Bug 2: clean() doesn't lower-case — "Dog." and "dog" won't be treated as the same
print("Test case-insensitive unique:")
r = summarize("Dog dog DOG")
print(f"  Result: {r}")  # Expected: unique=1

# Bug 3: Division by zero on empty input
print("Test empty input:")
try:
    r = summarize("")
    print(f"  Result: {r}")  # Expected: words=0, unique=0, avg_len=0.0
except ZeroDivisionError as e:
    print(f"  ERROR ZeroDivisionError: {e}")

# Bug 4: Punctuation-only tokens should not count as words
print("Test punctuation-only tokens:")
r = summarize("hello ... world")
print(f"  Result: {r}")  # Expected: words=2

# Combined test
print("Test combined (Dog. and dog):")
r = summarize("Dog. dog")
print(f"  Result: {r}")  # Expected: words=2, unique=1, avg_len=3.0
