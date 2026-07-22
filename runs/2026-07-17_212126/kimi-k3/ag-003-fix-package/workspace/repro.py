"""Verify textstats.summarize against the specification."""
from textstats import summarize

cases = [
    ("whitespace split (tabs/newlines/multi-space)",
     "a\tb  c\nd", {"words": 4, "unique": 4, "avg_len": 1.0}),
    ("case-insensitive unique + punct strip",
     "Dog. dog DOG!", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("punctuation-only token is not a word",
     "hello ... world !", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("empty input must not raise",
     "", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("no-word input must not raise",
     "  ... \t\n ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("avg rounding (7/3 = 2.33)",
     "aa bbb cc", {"words": 3, "unique": 3, "avg_len": 2.33}),
    ("mixed punctuation and case",
     '"Hello," he said. HELLO!', {"words": 4, "unique": 3, "avg_len": 4.0}),
    ("all punct chars stripped (8/3 = 2.67)",
     "(wow); 'yes'? \"no\".", {"words": 3, "unique": 3, "avg_len": 2.67}),
    ("inner punctuation kept (11/2 = 5.5)",
     "don't e-mail", {"words": 2, "unique": 2, "avg_len": 5.5}),
]

ok = True
for name, text, expected in cases:
    try:
        got = summarize(text)
    except Exception as e:
        print(f"[FAIL] {name}: raised {type(e).__name__}: {e}")
        ok = False
        continue
    status = "ok" if got == expected else "FAIL"
    if got != expected:
        ok = False
    print(f"[{status}] {name}: got {got}, expected {expected}")

print("\nALL PASS" if ok else "\nFAILURES PRESENT")
