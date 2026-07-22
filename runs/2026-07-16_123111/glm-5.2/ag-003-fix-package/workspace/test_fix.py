from textstats import summarize

cases = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("Dog. dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("Hello, world! (hello)", {"words": 3, "unique": 2, "avg_len": 5.0}),
    ("a  b\tc\n\nd", {"words": 4, "unique": 4, "avg_len": 1.0}),
    ("... !!! ???", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("'quoted' (paren)", {"words": 2, "unique": 2, "avg_len": 5.5}),
    ('"Dog." and \'dog\' are the same.', {"words": 6, "unique": 5, "avg_len": 3.17}),
]

for text, expected in cases:
    got = summarize(text)
    status = "OK" if got == expected else "FAIL"
    print(f"{status}: {text!r} -> {got} (expected {expected})")
