from textstats import summarize

def run_tests():
    assert summarize("") == {"words": 0, "unique": 0, "avg_len": 0.0}
    assert summarize("   \t\n\r\v\f  ") == {"words": 0, "unique": 0, "avg_len": 0.0}
    assert summarize(".,;:!?\"'()") == {"words": 0, "unique": 0, "avg_len": 0.0}
    assert summarize("...   ???   !!!") == {"words": 0, "unique": 0, "avg_len": 0.0}
    
    # "Dog." and "dog" are the same word.
    # A token that is only punctuation does not count as a word at all
    res = summarize('Dog. and "dog" ...')
    assert res == {"words": 2, "unique": 2, "avg_len": 3.0}, f"Got {res}"
    # wait: words: "Dog." -> "Dog" (len 3), "and" -> "and" (len 3), '"dog"' -> "dog" (len 3)
    # wait: distinct words: Dog and dog are the same word! So distinct words: 'dog', 'and' -> unique = 2.
    # total words: Dog, and, dog -> 3 words!
    res = summarize('Dog. and "dog" ...')
    assert res == {"words": 3, "unique": 2, "avg_len": 3.0}, f"Got {res}"
    
    # Multiple whitespace separation
    res = summarize("hello   \t\n  world")
    assert res == {"words": 2, "unique": 2, "avg_len": 5.0}

    # Internal punctuation: e.g. "don't" -> leading/trailing punctuation stripped, internal remains
    res = summarize("don't")
    assert res == {"words": 1, "unique": 1, "avg_len": 5.0}
    
    # Rounding check
    # lengths: 1, 2 -> avg 1.5
    assert summarize("a bb")["avg_len"] == 1.5
    # lengths: 1, 1, 2 -> avg 4/3 = 1.333... -> 1.33
    assert summarize("a b cc")["avg_len"] == 1.33
    # lengths: 1, 2, 2 -> avg 5/3 = 1.666... -> 1.67
    assert summarize("a bb cc")["avg_len"] == 1.67

    # Type check
    r = summarize("")
    assert isinstance(r["words"], int)
    assert isinstance(r["unique"], int)
    assert isinstance(r["avg_len"], float)

    print("All tests passed successfully!")

if __name__ == "__main__":
    run_tests()
