from textstats import summarize

cases = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   \n\t  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("Dog. dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("a\tb\nc  d", {"words": 4, "unique": 4, "avg_len": 1.0}),
    ('"Hello," she said...', {"words": 3, "unique": 3, "avg_len": round((5+3+4)/3, 2)}),
    ("!!! ??? ...", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("Hi.", {"words": 1, "unique": 1, "avg_len": 2.0}),
    # one(3) two(3) two(3) THREE(5) three(5) -> avg = 19/5 = 3.8
    ("one two two THREE three", {"words": 5, "unique": 3, "avg_len": 3.8}),
]

ok = True
for text, expected in cases:
    got = summarize(text)
    status = "PASS" if got == expected else f"FAIL (expected {expected})"
    if got != expected:
        ok = False
    print(f"{status} summarize({text!r}) -> {got}")

print("\nALL PASS" if ok else "\nSOME FAILURES")
