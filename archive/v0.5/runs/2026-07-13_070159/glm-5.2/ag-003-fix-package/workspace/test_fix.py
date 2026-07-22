from textstats import summarize

cases = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("Dog. dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ('"Hello," (world)!', {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("one\ttwo\nthree", {"words": 3, "unique": 3, "avg_len": round((3+3+5)/3, 2)}),
    ("a... b", {"words": 2, "unique": 2, "avg_len": 1.0}),
    ("...", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("  multiple   spaces  here  ", {"words": 3, "unique": 3, "avg_len": round((8+6+4)/3, 2)}),
]

ok = True
for text, expected in cases:
    got = summarize(text)
    status = "OK" if got == expected else "FAIL"
    if got != expected:
        ok = False
    print(f"{status}: {text!r} -> {got} (expected {expected})")

print("ALL PASS" if ok else "SOME FAILED")
