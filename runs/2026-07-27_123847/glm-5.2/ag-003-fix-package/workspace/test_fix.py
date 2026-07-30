from textstats import summarize

cases = [
    ("Hello world!", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("Dog.  dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("Hello\tworld\nfoo bar", {"words": 4, "unique": 4, "avg_len": 4.0}),
    ("   \t \n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("\"(quoted)\" ... text", {"words": 2, "unique": 2, "avg_len": (6 + 4) / 2}),
    ("word  word", {"words": 2, "unique": 1, "avg_len": 4.0}),
    ("'tis 'tis", {"words": 2, "unique": 1, "avg_len": 3.0}),
]

ok = True
for text, expected in cases:
    result = summarize(text)
    exp = {k: v for k, v in expected.items()}
    match = result == exp
    if not match:
        ok = False
    print(f"{'PASS' if match else 'FAIL'}: {text!r}")
    if not match:
        print(f"  expected: {exp}")
        print(f"  got:      {result}")

print("\nAll passed!" if ok else "\nSome tests failed.")
