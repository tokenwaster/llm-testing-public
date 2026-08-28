from textstats import summarize

cases = [
    # (input, expected)
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("\t\n \t", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("...", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("'()\"'", {"words": 0, "unique": 0, "avg_len": 0.0}),  # only PUNCT chars -> no words
    ("[]", {"words": 1, "unique": 1, "avg_len": 2.0}),       # brackets not in PUNCT list -> counts as word
    ("The quick brown fox", {"words": 4, "unique": 4, "avg_len": 4.5}),
    ("a bb ccc dddd", {"words": 4, "unique": 4, "avg_len": 2.5}),
    ("Dog. dog DOG cat", {"words": 4, "unique": 2, "avg_len": 3.0}),
    ('"Hello," said the "world"', {"words": 4, "unique": 4, "avg_len": 4.5}),
    ("one\ttwo\nthree   four", {"words": 4, "unique": 4, "avg_len": 3.75}),
]

all_ok = True
for text, expected in cases:
    got = summarize(text)
    ok = got == expected
    all_ok = all_ok and ok
    print(f"{'OK ' if ok else 'FAIL'} {text!r} -> {got}  (expected {expected})")

print("\nALL PASS" if all_ok else "\nSOME FAILED")
