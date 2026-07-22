from textstats import summarize

tests = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("Dog. dog cat", {"words": 3, "unique": 2, "avg_len": 3.0}),
    ("hello\tworld\n\nworld", {"words": 3, "unique": 2, "avg_len": 5.0}),
    ("... !!! ()", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("(hello) world!", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("a bb ccc", {"words": 3, "unique": 3, "avg_len": 2.0}),
]

for text, expected in tests:
    got = summarize(text)
    status = "OK" if got == expected else "FAIL"
    print(f"{status}: {text!r} -> {got} (expected {expected})")
