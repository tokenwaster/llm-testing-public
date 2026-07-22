from textstats import summarize

def test():
    # Test Case 1: Basic functionality and whitespace
    res1 = summarize("Hello world")
    print(f"Test 1 (Basic): {res1}")
    assert res1 == {"words": 2, "unique": 2, "avg_len": 5.0}

    # Test Case 2: Multiple whitespaces and different types of whitespace
    res2 = summarize("Hello   world\nthis\tis\tme")
    print(f"Test 2 (Whitespaces): {res2}")
    assert res2 == {"words": 5, "unique": 5, "avg_len": 3.6}

    # Test Case 3: Punctuation and case-insensitivity
    res3 = summarize("Dog. dog, DOG! (dog)")
    print(f"Test 3 (Punctuation/Case): {res3}")
    assert res3 == {"words": 4, "unique": 1, "avg_len": 3.0}

    # Test Case 4: Only punctuation
    res4 = summarize("..., !!! ???")
    print(f"Test 4 (Only Punctuation): {res4}")
    assert res4 == {"words": 0, "unique": 0, "avg_len": 0.0}

    # Test Case 5: Empty input
    res5 = summarize("")
    print(f"Test 5 (Empty Input): {res5}")
    assert res5 == {"words": 0, "unique": 0, "avg_len": 0.0}

    # Test Case 6: Mixed punctuation and words
    res6 = summarize("Hello, world! This is a test.")
    print(f"Test 6 (Mixed): {res6}")
    assert res6 == {"words": 6, "unique": 6, "avg_len": 3.5}

if __name__ == "__main__":
    test()
