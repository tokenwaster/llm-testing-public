import textstats

def test_summarize():
    # Test 1: basic
    res = textstats.summarize("Dog. dog")
    print("Test 1:", res)
    assert res == {"words": 2, "unique": 1, "avg_len": 3.0}

    # Test 2: whitespace
    res = textstats.summarize("Dog.\t\ndog")
    print("Test 2:", res)
    assert res == {"words": 2, "unique": 1, "avg_len": 3.0}

    # Test 3: only punctuation
    res = textstats.summarize("... Dog. !!! dog ...")
    print("Test 3:", res)
    assert res == {"words": 2, "unique": 1, "avg_len": 3.0}

    # Test 4: empty input
    res = textstats.summarize("")
    print("Test 4:", res)
    assert res == {"words": 0, "unique": 0, "avg_len": 0.0}

    # Test 5: input with only punctuation
    res = textstats.summarize("!!! ...")
    print("Test 5:", res)
    assert res == {"words": 0, "unique": 0, "avg_len": 0.0}

    print("All tests passed!")

if __name__ == "__main__":
    test_summarize()
