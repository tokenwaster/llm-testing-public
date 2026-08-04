from textstats import summarize

cases = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   \t\n ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("...", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),
    ("a\tb\nc  d", {"words": 4, "unique": 4, "avg_len": 1.0}),
    ("Hello, world! Hello ... (world)", {"words": 4, "unique": 2, "avg_len": 5.0}),
    ("one two three", {"words": 3, "unique": 3, "avg_len": 3.67}),
]

ok = True
for text, want in cases:
    got = summarize(text)
    status = "PASS" if got == want else "FAIL"
    if got != want:
        ok = False
    print(f"{status} {text!r}: got={got} want={want}")

print("ALL PASS" if ok else "FAILURES")
