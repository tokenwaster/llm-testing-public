from textstats import summarize

# Test 1: any whitespace separation (tabs, newlines, multiple spaces)
print("Test1:", summarize("dog dog\tdog\n  cat"))
# expected words=4 unique=2 avg_len = (3+3+3+3)/4 = 3.0

# Test 2: case-insensitive uniqueness + punctuation stripping
print("Test2:", summarize('Dog. "dog" CAT'))
# cleaned words: Dog, dog, CAT -> lowercased {dog, cat} unique=2
# avg_len over all words (3+3+3)/3 = 3.0

# Test 3: token that is only punctuation should not count
print("Test3:", summarize('... !!! ???'))
# expected words=0 unique=0 avg_len=0.0

# Test 4: empty input must not raise
print("Test4:", summarize(""))
# expected words=0 unique=0 avg_len=0.0
