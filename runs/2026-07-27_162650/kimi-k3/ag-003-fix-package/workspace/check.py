from textstats import summarize

cases = [
    ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("Dog. dog DOG!", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("a\tb\nc  d", {"words": 4, "unique": 4, "avg_len": 1.0}),
    ("... ,,, !", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   \n\t  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ('"Hello," she said.', {"words": 3, "unique": 3, "avg_len": round((5 + 3 + 4) / 3, 2)}),
    ("(wow) 'wow' wow.", {"words": 3, "unique": 1, "avg_len": 3.0}),
]

for text, expected in cases:
    try:
        got = summarize(text)
    except Exception as e:
        got = f"RAISED {type(e).__name__}: {e}"
    status = "OK  " if got == expected else "FAIL"
    print(f"{status} {text!r:35} -> {got}  (expected {expected})")
