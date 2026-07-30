from textstats import summarize


def test(text, expected):
    result = summarize(text)
    assert result == expected, f"{text!r}: got {result}, expected {expected}"


test("Dog. dog dog", {"words": 3, "unique": 1, "avg_len": 3.0})
test("Hello, world!", {"words": 2, "unique": 2, "avg_len": 5.0})
test("   ...   ", {"words": 0, "unique": 0, "avg_len": 0.0})
test("", {"words": 0, "unique": 0, "avg_len": 0.0})
test("One\tTWO\nthree", {"words": 3, "unique": 3, "avg_len": 3.67})
test("cat, CAT; (Cat). 'CAT'!", {"words": 4, "unique": 1, "avg_len": 3.0})
test("a b c", {"words": 3, "unique": 3, "avg_len": 1.0})

print("All tests passed.")
