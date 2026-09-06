from textstats import summarize

CASES = [
    # (text, expected)
    ("Hello world hello", {"words": 3, "unique": 2, "avg_len": 5.0}),
    ("Dog. dog DOG!", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("a\tb\nc   d", {"words": 4, "unique": 4, "avg_len": 1.0}),
    ("  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("... !!! ???", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ('"Hi," said Tom; (loudly)!', {"words": 4, "unique": 4, "avg_len": 3.75}),
    ("one", {"words": 1, "unique": 1, "avg_len": 3.0}),
    ("aa bbb", {"words": 2, "unique": 2, "avg_len": 2.5}),
    ("The quick brown fox jumps over the lazy dog",
     {"words": 9, "unique": 8, "avg_len": 3.89}),
    ("\t\n  \t ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("don't stop", {"words": 2, "unique": 2, "avg_len": 4.5}),
    # punctuation-only tokens are not words at all
    ("a . b , c", {"words": 3, "unique": 3, "avg_len": 1.0}),
    ("...", {"words": 0, "unique": 0, "avg_len": 0.0}),
    # case-insensitivity across punctuation
    ('"The" the THE; the.', {"words": 4, "unique": 1, "avg_len": 3.0}),
    # rounding to 2 decimals
    ("aaa bbbb ccccccc", {"words": 3, "unique": 3, "avg_len": 4.67}),
    # mixed whitespace + repeated words
    ("foo\tfoo\nfoo  bar", {"words": 4, "unique": 2, "avg_len": 3.0}),
]

fails = 0
for text, expected in CASES:
    try:
        got = summarize(text)
    except Exception as e:  # noqa: BLE001
        got = f"{type(e).__name__}: {e}"
    ok = got == expected
    if not ok:
        fails += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {text!r}\n       expected={expected}\n       got     ={got}")

print(f"\n{fails} failing case(s) out of {len(CASES)}")
