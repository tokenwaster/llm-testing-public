import textstats.core

def run_test(text, expected):
    result = textstats.core.summarize(text)
    print(f"Input: '{repr(text)}'")
    print(f"Expected: {expected}")
    print(f"Got:      {result}")
    assert result == expected, f"Failed for input '{repr(text)}'. Expected {expected}, got {result}"
    print("--- Test Passed ---")

# 1. Empty input
run_test("", {"words": 0, "unique": 0, "avg_len": 0.0})

# 2. Input with only punctuation/whitespace (should result in 0 words)
run_test(".,;:!?", {"words": 0, "unique": 0, "avg_len": 0.0})
run_test(" \t\n ", {"words": 0, "unique": 0, "avg_len": 0.0})

# 3. Standard sentence (Case-insensitivity and punctuation stripping)
# Words: Hello, world, dog. Dog! -> hello, world, dog, dog
# Unique: {hello, world, dog} -> 3
# Lengths: 5 + 5 + 3 + 3 = 16. Count: 4. Avg: 16/4 = 4.0
run_test("Hello world dog. Dog!", {"words": 4, "unique": 3, "avg_len": 4.0})

# 4. Complex whitespace and punctuation (Multiple spaces, tabs, newlines)
# Words: Test\tcase.\nAnother! -> test, case, another
# Unique: {test, case, another} -> 3
# Lengths: 4 + 4 + 7 = 15. Count: 3. Avg: 15/3 = 5.0
run_test("Test\tcase.\nAnother!", {"words": 3, "unique": 3, "avg_len": 5.0})

# 5. Single word test (punctuation only)
run_test(".", {"words": 0, "unique": 0, "avg_len": 0.0})

# 6. Test with mixed case and punctuation at ends
# Words: Word. word? WORD! -> word, word, word
# Unique: {word} -> 1
# Lengths: 4 + 4 + 4 = 12. Count: 3. Avg: 12/3 = 4.0
run_test("Word. word? WORD!", {"words": 3, "unique": 1, "avg_len": 4.0})