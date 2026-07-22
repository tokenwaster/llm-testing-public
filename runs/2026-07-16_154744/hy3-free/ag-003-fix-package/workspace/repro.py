from textstats import summarize

cases = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   \n\t  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("Dog. dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("Hello, world! (cat) cat.", {"words": 4, "unique": 3, "avg_len": 4.0}),
    ("a b c d e", {"words": 5, "unique": 5, "avg_len": 1.0}),
    ("...???", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("tab\tnewline\nsep", {"words": 3, "unique": 3, "avg_len": 4.33}),
    ("The dog. THE DOG! (dog)", {"words": 5, "unique": 2, "avg_len": 3.0}),
]

all_ok = True
for text, expected in cases:
    try:
        got = summarize(text)
    except Exception as e:
        print(f"FAIL (raised) {text!r}: {e}")
        all_ok = False
        continue
    ok = got == expected
    if not ok:
        all_ok = False
    print(f"{'OK ' if ok else 'FAIL'} {text!r} -> {got} (expected {expected})")

print("ALL OK" if all_ok else "SOME FAILED")
