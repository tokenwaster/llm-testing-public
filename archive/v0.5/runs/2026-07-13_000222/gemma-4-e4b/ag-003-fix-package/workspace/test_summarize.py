import textstats.core as ts

def run_test(text, expected):
    result = ts.summarize(text)
    print(f"--- Testing input: '{repr(text)}' ---")
    print(f"Expected: {expected}")
    print(f"Got:       {result}")
    if result == expected:
        print("PASS")
    else:
        print("FAIL")

# Test Case 1: Basic functionality (spaces, punctuation)
run_test("Hello world. This is a test.", {"words": 5, "unique": 4, "avg_len": 3.2}) # Words: Hello(5), world(5), This(4), is(2), a(1), test(4). Unique: hello, world, this, is, a, test (6 unique if case-insensitive) Wait, let's count manually.
# Input: "Hello world. This is a test."
# Tokens: ["Hello", "world.", "This", "is", "a", "test."]
# Cleaned words: ["Hello", "world", "This", "is", "a", "test"] (6 words)
# Unique (lower): {"hello", "world", "this", "is", "a", "test"} (6 unique)
# Lengths: 5 + 5 + 4 + 2 + 1 + 4 = 21. Avg: 21/6 = 3.5.
run_test("Hello world. This is a test.", {"words": 6, "unique": 6, "avg_len": 3.5})

# Test Case 2: Whitespace handling (tabs, newlines, multiple spaces)
run_test("Word1\tWord2 \n Word3", {"words": 3, "unique": 3, "avg_len": 4.0}) # Words: Word1(5), Word2(5), Word3(5). Total length: 15. Avg: 5.0. Wait, the example is wrong.
# Input: "Word1\tWord2 \n Word3"
# Tokens (split()): ["Word1", "Word2", "Word3"] (3 words)
# Unique: {"word1", "word2", "word3"} (3 unique)
# Lengths: 5 + 5 + 5 = 15. Avg: 15/3 = 5.0.
run_test("Word1\tWord2 \n Word3", {"words": 3, "unique": 3, "avg_len": 5.0})

# Test Case 3: Case-insensitivity and punctuation stripping
run_test("Dog. dog's book; BOOK!", {"words": 3, "unique": 2, "avg_len": 3.0})
# Tokens: ["Dog.", "dog's", "book;", "BOOK!"] -> Wait, the example only has 3 words in my manual count. Let's re-evaluate based on tokens.
# Input: "Dog. dog's book; BOOK!"
# Tokens (split()): ["Dog.", "dog's", "book;", "BOOK!"] (4 tokens)
# Cleaned words: ["Dog", "dog's", "book", "BOOK"] (4 words)
# Unique (lower): {"dog", "dog's", "book"} (3 unique). Wait, 'dog.' and 'dog' are the same. The spec says leading/trailing punctuation is ignored.
# Let's assume clean handles this:
# "Dog." -> "Dog"
# "dog's" -> "dog's" (apostrophe usually kept)
# "book;" -> "book"
# "BOOK!" -> "BOOK"
# If the spec means *only* leading/trailing punctuation is stripped, then 'dog's' should remain.
# Let's assume standard stripping:
# 1. "Dog." -> "Dog" (Length 3)
# 2. "dog's" -> "dog's" (Length 5) - assuming ' is not in PUNCT list, which it isn't defined as being stripped by the current implementation `PUNCT = ".,;:!?\"'()"` but wait, it *is* included!
# Let's check: `PUNCT = ".,;:!?\"'()"` -> Yes, `'` is in PUNCT.
# If ' is stripped:
# 1. "Dog." -> "Dog" (L=3)
# 2. "dog's" -> "dogs" (L=4). This seems wrong based on typical word definition.

# Re-reading the spec for unique: ignoring leading and trailing punctuation (`.,;:!?"'()`): `"Dog."` and `"dog"` are the same word.
# If ' is stripped, then "dog's" becomes "dogs". Let's assume the intent was to strip only standard sentence punctuation, but since I used `PUNCT = ".,;:!?\"'()"` in helpers.py, I must stick to that definition.

# Test Case 3 Re-run with current implementation:
# Input: "Dog. dog's book; BOOK!"
# Tokens: ["Dog.", "dog's", "book;", "BOOK!"]
# Cleaned words (using strip(PUNCT)):
# 1. "Dog." -> "Dog"
# 2. "dog's" -> "dogs" (because ' is stripped)
# 3. "book;" -> "book"
# 4. "BOOK!" -> "BOOK"
# Words: ["Dog", "dogs", "book", "BOOK"] (4 words)
# Unique (lower): {"dog", "dogs", "book"} (3 unique). Wait, 'dog' vs 'dogs'. This is a major ambiguity in the spec/implementation.

# Let's assume the goal of the test case was: Dog -> dog, book -> book, BOOK -> book.
# If we stick strictly to the code logic and the provided punctuation set:
# Words: ["Dog", "dogs", "book", "BOOK"] (4 words)
# Unique (lower): {"dog", "dogs", "book", "book"} -> {"dog", "dogs", "book"} (3 unique). This seems like a bug in my understanding or the spec.

# Let's assume the example intended: Dog, dog, book, book.
# If we use simpler input to test case-insensitivity and stripping:
run_test("Apple. apple! APPLE?", {"words": 3, "unique": 1, "avg_len": 5.0})
# Tokens: ["Apple.", "apple!", "APPLE?"] (3 words)
# Cleaned words: ["Apple", "apple", "APPLE"] (3 words)
# Unique (lower): {"apple"} (1 unique). Correct.
# Lengths: 5 + 5 + 5 = 15. Avg: 15/3 = 5.0.

# Test Case 4: Only punctuation input
run_test(".,;!?", {"words": 0, "unique": 0, "avg_len": 0.0})

# Test Case 5: Empty input
run_test("", {"words": 0, "unique": 0, "avg_len": 0.0})

# Test Case 6: Mixed case and length calculation
run_test("a B ccc DDD", {"words": 4, "unique": 3, "avg_len": 2.5})
# Words: ["a", "B", "ccc", "DDD"] (4 words)
# Unique (lower): {"a", "b", "ccc", "ddd"} -> Wait, 'B' vs 'b'.
# Unique (lower): {"a", "b", "c", "d"} (4 unique).
# Lengths: 1 + 1 + 3 + 3 = 8. Avg: 8/4 = 2.0.
run_test("a B ccc DDD", {"words": 4, "unique": 4, "avg_len": 2.0})