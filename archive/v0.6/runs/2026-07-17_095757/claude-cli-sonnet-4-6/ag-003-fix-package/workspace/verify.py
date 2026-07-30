from textstats import summarize

cases = [
    ("basic", summarize("hello world"), {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("tabs+newlines", summarize("hello\tworld\nnewline"), {"words": 3, "unique": 3, "avg_len": 5.67}),
    ("case-insensitive punct", summarize("Dog. dog DOG"), {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("punct-only token", summarize("hello ... world"), {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("empty", summarize(""), {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("avg_len", summarize("cat. do"), {"words": 2, "unique": 2, "avg_len": 2.5}),
]

all_ok = True
for name, got, want in cases:
    ok = got == want
    status = "OK" if ok else "FAIL"
    print(f"{status} {name}: got={got} want={want}")
    if not ok:
        all_ok = False

print("All passed!" if all_ok else "FAILURES above")
