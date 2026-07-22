from textstats import summarize

cases = {
    "Dog. dog\tcat\nCAT!": {"words": 4, "unique": 2, "avg_len": 3.0},
    "   ... \t !!!\n": {"words": 0, "unique": 0, "avg_len": 0.0},
    "": {"words": 0, "unique": 0, "avg_len": 0.0},
    "(Hello), 'WORLD!' hello": {"words": 3, "unique": 2, "avg_len": 5.0},
    "a bb ccc dddd": {"words": 4, "unique": 4, "avg_len": 2.5},
}

for text, expected in cases.items():
    actual = summarize(text)
    print(repr(text), "=>", actual)
    assert actual == expected, (actual, expected)

print("All checks passed")
