from textstats import summarize

def test():
    # Test 1: Whitespace separation (multiple spaces, tabs, newlines)
    # Current code might fail because it uses .split(" ")
    res1 = summarize("hello   world\ntest\tagain")
    print(f"Test 1 (whitespace): {res1}")
    assert res1["words"] == 4

    # Test 2: Case-insensitivity for unique words
    # Current code might fail because it doesn't lower() before set()
    res2 = summarize("Dog dog DOG")
    print(f"Test 2 (case-insensitive): {res2}")
    assert res2["unique"] == 1

    # Test 3: Punctuation stripping and only punctuation tokens
    # "Dog." and "dog" are the same. "!!!" should not count as a word.
    res3 = summarize("Dog. dog !!!")
    print(f"Test 3 (punctuation): {res3}")
    assert res3["words"] == 2
    assert res3["unique"] == 1

    # Test 4: Empty input or no words
    # Current code might raise ZeroDivisionError
    try:
        res4 = summarize("")
        print(f"Test 4 (empty string): {res4}")
        assert res4 == {"words": 0, "unique": 0, "avg_len": 0.0}
    except Exception as e:
        print(f"Test 4 (empty string) failed with error: {e}")

    # Test 5: Average length rounding
    res5 = summarize("abc defgh") # lengths 3 and 5, avg 4.0
    print(f"Test 5 (avg_len): {res5}")
    assert res5["avg_len"] == 4.0

    res6 = summarize("a bcde") # lengths 1 and 4, avg 2.5
    print(f"Test 6 (avg_len): {res6}")
    assert res6["avg_len"] == 2.5

    res7 = summarize("a bbbbbbb") # lengths 1 and 7, avg 4.0
    # Let's try something that results in a non-integer average
    res8 = summarize("ab cde fghij") # lengths 2, 3, 5 -> sum 10, count 3 -> 3.333...
    print(f"Test 8 (avg_len rounding): {res8}")
    assert res8["avg_len"] == 3.33

if __name__ == "__main__":
    test()
