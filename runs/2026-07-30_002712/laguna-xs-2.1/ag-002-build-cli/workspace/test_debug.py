import re

text = """Hello, World!
This is a test.

Hello hello HELLO world.
Test-test_test
123abc abc123
End."""

# Extract words
lowered = text.lower()
words = re.findall(r'[a-z]+', lowered)
print("Words found:", words)
print("Total count:", len(words))
print("Line count:", len(text.split('\n')))