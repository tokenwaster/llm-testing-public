from textstats import summarize

def test():
    # Test whitespace and multiple spaces
    assert summarize("hello   world") == {"words": 2, "unique": 2, "avg_len": 5.0}
    assert summarize("hello\nworld\tagain") == {"words": 3, "unique": 3, "avg_len": 5.0}

    # Test punctuation and case-insensitivity
    assert summarize("Dog. dog, DOG!") == {"words": 3, "unique": 1, "avg_len": 3.0}
    assert summarize("Hello, world.") == {"words": 2, "unique": 2, "avg_len": 5.0}

    # Test punctuation-only tokens (should not count)
    assert summarize("..., hello!") == {"words": 1, "unique": 1, "avg_len": 5.0}
    assert summarize("...") == {"words": 0, "unique": 0, "avg_len": 0.0}

    # Test empty input or no words
    assert summarize("") == {"words": 0, "unique": 0, "avg_len": 0.0}
    assert summarize("   ") == {"words": 0, "unique": 0, "avg_len": 0.0}
    assert summarize("!!! ???") == {"words": 0, "unique": 0, "avg_len": 0.0}

    print("All tests passed!")

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
