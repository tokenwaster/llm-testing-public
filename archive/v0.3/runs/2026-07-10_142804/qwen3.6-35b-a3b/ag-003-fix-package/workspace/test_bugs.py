from textstats import summarize

# Bug 1: tokenize only splits on single spaces, not any whitespace
text1 = "hello\tworld\nfoo  bar"
result1 = summarize(text1)
print(f"Test 1 (whitespace): {result1}")
print(f"  Expected words=4, got words={result1['words']}")

# Bug 2: unique should be case-insensitive
text2 = "Dog dog DOG"
result2 = summarize(text2)
print(f"Test 2 (case-insensitive unique): {result2}")
print(f"  Expected unique=1, got unique={result2['unique']}")

# Bug 3: empty input should not raise
text3 = ""
try:
    result3 = summarize(text3)
    print(f"Test 3 (empty input): {result3}")
except ZeroDivisionError:
    print("Test 3 (empty input): ZeroDivisionError raised!")

# Bug 4: punctuation-only tokens should not count
text4 = "!!! ... ,,, hello"
result4 = summarize(text4)
print(f"Test 4 (punctuation-only tokens): {result4}")
print(f"  Expected words=1, got words={result4['words']}")

# Bug 5: punctuation stripping
text5 = "Hello, world!"
result5 = summarize(text5)
print(f"Test 5 (punctuation stripping): {result5}")
print(f"  Expected words=2, unique=2, avg_len=5.0")
