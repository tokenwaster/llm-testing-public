"""Quick reproduction / verification script for textstats.summarize."""
from textstats import summarize

CASES = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("... ! ?", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("Dog. dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("a\tb\nc  d", {"words": 4, "unique": 4, "avg_len": 1.0}),
    ("hello, world! 'quoted' (paren)", {"words": 4, "unique": 4, "avg_len": 5.25}),
    # 6 tokens: one(3) two(3) two(3) three(5) three(5) three(5) -> 24/6 = 4.0
    ("one two, two; three: three? three!",
     {"words": 6, "unique": 3, "avg_len": 4.0}),
    # hi(2), there(5) -> 7/2 = 3.5
    ("hi...   ...there", {"words": 2, "unique": 2, "avg_len": 3.5}),
    # punctuation-only tokens between real words must not count
    ("cat , dog . ,", {"words": 2, "unique": 2, "avg_len": 3.0}),
    # mixed case + punctuation + extra whitespace
    ("\n\tHello,  HELLO... hello!\n", {"words": 3, "unique": 1, "avg_len": 5.0}),
    # apostrophes/quotes stripped from both ends only
    ("'tis \"rock\" don't", {"words": 3, "unique": 3,
     "avg_len": round((3 + 4 + 5) / 3, 2)}),
    # rounding check: 1, 2, 2 -> 5/3 = 1.666... -> 1.67
    ("a bb cc", {"words": 3, "unique": 3, "avg_len": 1.67}),
]

failed = 0
for text, expected in CASES:
    try:
        got = summarize(text)
    except Exception as e:
        print(f"FAIL  {text!r}: raised {type(e).__name__}: {e}")
        failed += 1
        continue
    status = "ok  " if got == expected else "FAIL"
    if got != expected:
        failed += 1
    print(f"{status}  {text!r}: got {got}, expected {expected}")

print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
raise SystemExit(1 if failed else 0)
