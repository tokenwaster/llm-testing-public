"""Reproduce bugs before fixing."""
from textstats import summarize

# Bug 1: only splits on spaces, not all whitespace
print("Test tabs/newlines:")
result = summarize("hello\tworld\nfoo")
print(f"  words={result['words']} (expected 3)")

# Bug 2: empty input causes ZeroDivisionError
print("\nTest empty input:")
try:
    result = summarize("")
    print(f"  {result}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

# Bug 3: punctuation-only tokens should not count
print("\nTest punctuation only:")
result = summarize("... ,,, !!!")
print(f"  words={result['words']} (expected 0), unique={result['unique']}, avg_len={result['avg_len']}")

# Case-insensitive + punctuation stripping
print("\nTest case+PUNCT:")
result = summarize('Dog. "dog" DOG!')
print(f"  {result} (expected words=3, unique=1)")
