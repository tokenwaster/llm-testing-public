from textstats import summarize

cases = [
    # (input, expected)
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("!!! ... ???", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("Dog. dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("a\tb\nc  d", {"words": 4, "unique": 4, "avg_len": 1.0}),
    # Hello(5) world(5) Hello(5) world(5) -> avg 5.0
    ('Hello, world! Hello "world".', {"words": 4, "unique": 2, "avg_len": 5.0}),
    ("it's a test.", {"words": 3, "unique": 3, "avg_len": 3.0}),
    ("(hi);", {"words": 1, "unique": 1, "avg_len": 2.0}),
    ("MiXeD mIxEd", {"words": 2, "unique": 1, "avg_len": 5.0}),
    ("one two three four", {"words": 4, "unique": 4, "avg_len": round((3+3+5+4)/4, 2)}),
    # spec example: "Dog." and "dog" are the same word
    ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),
    # punctuation-only tokens don't count in words or unique
    ("cat ... dog !!!", {"words": 2, "unique": 2, "avg_len": 3.0}),
    # mixed whitespace runs
    ("foo \t\n bar", {"words": 2, "unique": 2, "avg_len": 3.0}),
    # rounding to 2 decimals: (2+3+2)/3 = 2.333... -> 2.33
    ("ab cde fg", {"words": 3, "unique": 3, "avg_len": 2.33}),
]

ok = True
for text, expected in cases:
    try:
        got = summarize(text)
    except Exception as e:
        print(f"FAIL  {text!r}: raised {type(e).__name__}: {e}")
        ok = False
        continue
    if got != expected:
        print(f"FAIL  {text!r}: got {got}, expected {expected}")
        ok = False
    else:
        print(f"OK    {text!r}: {got}")

print("\nALL PASS" if ok else "\nFAILURES PRESENT")
