from textstats import summarize

# Basic test
print("Test 1 - basic:", summarize("Hello world"))
assert summarize("Hello world") == {"words": 2, "unique": 2, "avg_len": 5.0}

# Case-insensitive uniqueness with punctuation
print("Test 2 - case/punct:", summarize("Dog. dog DOG!"))
assert summarize("Dog. dog DOG!") == {"words": 3, "unique": 1, "avg_len": 3.0}

# Any whitespace
print("Test 3 - whitespace:", summarize("a\tb\n  c"))
assert summarize("a\tb\n  c") == {"words": 3, "unique": 3, "avg_len": 1.0}

# Only punctuation
print("Test 4 - punct only:", summarize("!!! ..."))
assert summarize("!!! ...") == {"words": 0, "unique": 0, "avg_len": 0.0}

# Empty
print("Test 5 - empty:", summarize(""))
assert summarize("") == {"words": 0, "unique": 0, "avg_len": 0.0}

# Mixed punctuation in word: "'hello'." -> "hello"
print("Test 6 - mixed punct:", summarize("'hello'. world!"))
assert summarize("'hello'. world!") == {"words": 2, "unique": 2, "avg_len": 5.0}

# Word counts including "it's" with apostrophe inside
print("Test 7 - apostrophe inside:", summarize("it's it's"))
assert summarize("it's it's") == {"words": 2, "unique": 1, "avg_len": 4.0}

print("All tests passed!")
