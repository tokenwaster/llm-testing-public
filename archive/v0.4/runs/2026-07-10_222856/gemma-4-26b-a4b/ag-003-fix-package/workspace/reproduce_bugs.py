from textstats import summarize

def test_summarize():
    test_cases = [
        # Case 1: Basic functionality
        ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
        # Case 2: Multiple whitespaces (tabs, newlines)
        ("Hello\tworld\nagain", {"words": 3, "unique": 3, "avg_len": 5.0}),
        # Case 3: Punctuation stripping and case-insensitivity
        ("Dog. dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
        # Case 4: Tokens that are only punctuation should not count as words
        ("!!! ???", {"words": 0, "unique": 0, "avg_len": 0.0}),
        # Case 5: Empty input
        ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
        # Case 6: Mixed punctuation and whitespace
        ("  Hello, world!  ", {"words": 2, "unique": 2, "avg_len": 5.0}),
        # Case 7: Different word lengths for average calculation
        ("a bb ccc", {"words": 3, "unique": 3, "avg_len": 2.0}),
    ]

    for i, (text, expected) in enumerate(test_cases):
        try:
            result = summarize(text)
            if result == expected:
                print(f"Test case {i+1} passed!")
            else:
                print(f"Test case {i+1} failed: expected {expected}, got {result}")
        except Exception as e:
            print(f"Test case {i+1} raised exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_summarize()
