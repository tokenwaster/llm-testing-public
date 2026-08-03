from textstats import summarize

cases = [
    ("hello world hello", {"words": 3, "unique": 2, "avg_len": 5.0}),
    ("Dog dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),       # case-insensitive unique
    ("dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),          # strip trailing punct, merge
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),                  # empty input
    ("!!! ...", {"words": 0, "unique": 0, "avg_len": 0.0}),          # only punctuation
    ("a\tb\nc", {"words": 3, "unique": 3, "avg_len": 1.0}),          # tabs & newlines
    ("hi  there   lots  of   spaces", {"words": 5, "unique": 5, "avg_len": 3.8}),
    ("'quoted' (words)", {"words": 2, "unique": 2, "avg_len": 5.5}),  # 'quoted'(6) + words(5) -> avg 5.5
    ("can't won't", {"words": 2, "unique": 2, "avg_len": 5.0}),       # inner apostrophes kept
    ("Hello, WORLD!\tHello.", {"words": 3, "unique": 2, "avg_len": 5.0}),
    ("one, two, THREE, four, four", {"words": 5, "unique": 4, "avg_len": 3.8}),
]

ok = True
for text, expected in cases:
    try:
        got = summarize(text)
    except Exception as e:
        got = f"RAISED {type(e).__name__}: {e}"
    match = "OK" if got == expected else "FAIL"
    if got != expected:
        ok = False
    print(f"[{match}] input={text!r}")
    print(f"        expected={expected}")
    print(f"        got     ={got}")

print("\nALL PASS" if ok else "\nSOME FAILED")
