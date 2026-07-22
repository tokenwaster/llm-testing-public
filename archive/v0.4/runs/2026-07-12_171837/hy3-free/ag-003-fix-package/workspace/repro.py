from textstats import summarize

cases = [
    ("Hello world hello", {"words": 3, "unique": 2, "avg_len": 5.0}),
    ("Dog. dog cat!", {"words": 3, "unique": 2, "avg_len": 3.0}),
    ("  multiple   spaces\ttab\nnewline ", {"words": 4, "unique": 4, "avg_len": 6.0}),
    ("!!! ??? ...", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
]

all_ok = True
for text, expected in cases:
    got = summarize(text)
    ok = got == expected
    all_ok &= ok
    print(f"{'OK ' if ok else 'FAIL'} {text!r} -> {got}")

print("ALL PASS" if all_ok else "SOME FAILED")
