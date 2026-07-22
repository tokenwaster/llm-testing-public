from textstats import summarize

cases = {
    "Dog. dog": {"words": 2, "unique": 1, "avg_len": 3.0},
    "a\tb\n c": {"words": 3, "unique": 3, "avg_len": 1.0},
    "!!! ...": {"words": 0, "unique": 0, "avg_len": 0.0},
    "": {"words": 0, "unique": 0, "avg_len": 0.0},
    "  HeLLo,  hello! world; ": {"words": 3, "unique": 2, "avg_len": 5.0},
}
for text, expected in cases.items():
    actual = summarize(text)
    print(repr(text), actual)
    assert actual == expected
