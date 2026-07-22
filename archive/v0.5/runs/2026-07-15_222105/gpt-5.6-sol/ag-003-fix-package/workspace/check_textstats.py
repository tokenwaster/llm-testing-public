from textstats import summarize

cases = [
    ("Dog. dog\tCAT\ncat!", {"words": 4, "unique": 2, "avg_len": 3.0}),
    ("... !!!", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("  Hello,   world! ", {"words": 2, "unique": 2, "avg_len": 5.0}),
]

for text, expected in cases:
    try:
        actual = summarize(text)
    except Exception as exc:
        actual = f"{type(exc).__name__}: {exc}"
    print(repr(text), "=>", actual, "expected", expected)
