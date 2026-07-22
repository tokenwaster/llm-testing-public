from textstats import summarize

def test():
    # Test 1: Multiple whitespaces and different whitespace characters
    res1 = summarize("Hello   world\nthis\tis\ta\ttest")
    print(f"Test 1 (multiple/different whitespaces): {res1}")
    assert res1 == {"words": 6, "unique": 6, "avg_len": 3.5}

    # Test 2: Case-insensitivity and punctuation
    res2 = summarize("Dog. dog DOG")
    print(f"Test 2 (case-insensitive/punctuation): {res2}")
    assert res2 == {"words": 3, "unique": 1, "avg_len": 3.0}

    # Test 3: Only punctuation tokens
    res3 = summarize("... , ; !!!")
    print(f"Test 3 (only punctuation): {res3}")
    assert res3 == {"words": 0, "unique": 0, "avg_len": 0.0}

    # Test 4: Empty input
    res4 = summarize("")
    print(f"Test 4 (empty input): {res4}")
    assert res4 == {"words": 0, "unique": 0, "avg_len": 0.0}

    # Test 5: Mixed punctuation and words
    res5 = summarize("Hello, world! This is a test.")
    print(f"Test 5 (mixed): {res5}")
    assert res5 == {"words": 6, "unique": 6, "avg_len": 3.5}

if __name__ == "__main__":
    test()
    print("All tests passed!")
