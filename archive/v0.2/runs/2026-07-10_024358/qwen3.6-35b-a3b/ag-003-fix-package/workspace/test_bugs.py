from textstats import summarize

# Test 1: Multiple whitespace types (tabs, newlines)
text1 = "hello\tworld\nfoo  bar"
result1 = summarize(text1)
print(f"Test 1 (whitespace): {result1}")
print(f"  Expected words=4, got words={result1['words']}")

# Test 2: Punctuation stripping
text2 = "Dog. cat Dog cat"
result2 = summarize(text2)
print(f"Test 2 (punctuation): {result2}")
print(f"  Expected words=4, unique=2, got words={result2['words']}, unique={result2['unique']}")

# Test 3: Only punctuation
text3 = "!!! ... ,,,"
result3 = summarize(text3)
print(f"Test 3 (only punctuation): {result3}")
print(f"  Expected words=0, unique=0, avg_len=0.0")

# Test 4: Empty input
text4 = ""
result4 = summarize(text4)
print(f"Test 4 (empty): {result4}")
print(f"  Expected words=0, unique=0, avg_len=0.0")

# Test 5: Case insensitivity
text5 = "Hello HELLO hello"
result5 = summarize(text5)
print(f"Test 5 (case): {result5}")
print(f"  Expected words=3, unique=1, got words={result5['words']}, unique={result5['unique']}")

# Test 6: avg_len calculation
text6 = "ab cd"
result6 = summarize(text6)
print(f"Test 6 (avg_len): {result6}")
print(f"  Expected avg_len=2.0, got avg_len={result6['avg_len']}")
