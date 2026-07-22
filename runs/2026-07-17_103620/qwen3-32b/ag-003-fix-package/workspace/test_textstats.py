import textstats.core

def test_summarize():
    assert textstats.core.summarize("") == {"words": 0, "unique": 0, "avg_len": 0.0}
    assert textstats.core.summarize("Dog dog!") == {"words": 2, "unique": 1, "avg_len": 3.0}
    assert textstats.core.summarize("Hello,\tworld!   Hello?\n") == {"words": 2, "unique": 1, "avg_len": 5.0}

if __name__ == "__main__":
    test_summarize()
    print("All tests passed!")