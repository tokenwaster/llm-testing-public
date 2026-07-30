from textstats import summarize

cases = {
    "Dog. dog": {"words": 2, "unique": 1, "avg_len": 3.0},
    "one\ttwo\nthree": {"words": 3, "unique": 3, "avg_len": 3.67},
    "... !?": {"words": 0, "unique": 0, "avg_len": 0.0},
    "": {"words": 0, "unique": 0, "avg_len": 0.0},
    "  'Hello,' (WORLD!) hello;  ": {"words": 3, "unique": 2, "avg_len": 5.0},
    "a bb ccc": {"words": 3, "unique": 3, "avg_len": 2.0},
}
for text, expected in cases.items():
    actual = summarize(text)
    assert actual == expected, (text, actual, expected)
    print(repr(text), actual)
print("All checks passed")
