from textstats import summarize

cases = [
    ("Dog. dog\tCAT\ncat!", {"words": 4, "unique": 2, "avg_len": 3.0}),
    ("  hello   world  ", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("... \t !!!\n()", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("'One,' TWO; two", {"words": 3, "unique": 2, "avg_len": 3.0}),
]

for text, expected in cases:
    actual = summarize(text)
    print(repr(text), actual)
    assert actual == expected, (actual, expected)
