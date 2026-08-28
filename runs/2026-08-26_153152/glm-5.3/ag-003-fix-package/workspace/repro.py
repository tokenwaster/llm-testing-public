from textstats import summarize

cases = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("Dog. dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("one\ttwo\nthree  four", {"words": 4, "unique": 4, "avg_len": 3.75}),  # 3+3+5+4=15/4
    ("a b c a", {"words": 4, "unique": 3, "avg_len": 1.0}),
    ("... !!! ()", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("(hello) world!", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("Hi, there; friend?", {"words": 3, "unique": 3, "avg_len": 4.33}),  # 13/3
    ("Don't stop", {"words": 2, "unique": 2, "avg_len": 4.5}),
    ("  spaced\tout\n\nbadly  ", {"words": 3, "unique": 3, "avg_len": 4.67}),  # 14/3
    ("a", {"words": 1, "unique": 1, "avg_len": 1.0}),
    (".,;:!?", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("The THE the. THE!", {"words": 4, "unique": 1, "avg_len": 3.0}),
    ('"quoted" (parenthesized)', {"words": 2, "unique": 2, "avg_len": 9.5}),  # 6+13=19/2
]

fails = 0
for text, expected in cases:
    try:
        got = summarize(text)
    except Exception as e:
        got = f"RAISED {type(e).__name__}: {e}"
    ok = got == expected
    fails += (not ok)
    print(("PASS" if ok else "FAIL"), repr(text), "->", got, "expected", expected)

# sanity checks on types / return shape
r = summarize("Hello")
assert set(r) == {"words", "unique", "avg_len"}, r
assert isinstance(r["words"], int) and isinstance(r["unique"], int) and isinstance(r["avg_len"], float)

print("\nfailures:", fails)
