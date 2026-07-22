"""Quick test of textstats.summarize against the spec."""
from textstats import summarize

cases = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}, "empty string"),
    ("   \n\t  ", {"words": 0, "unique": 0, "avg_len": 0.0}, "only whitespace"),
    ("hello world", {"words": 2, "unique": 2, "avg_len": 5.0}, "two simple words"),
    ("Dog. dog DOG!", {"words": 3, "unique": 1, "avg_len": 3.0}, "case + punct"),
    ("... !!!", {"words": 0, "unique": 0, "avg_len": 0.0}, "only punctuation"),
    ("a\tb\nc", {"words": 3, "unique": 3, "avg_len": 1.0}, "tab/newline sep"),
    ("  multiple   spaces  between  ", {"words": 3, "unique": 3, "avg_len": 7.0}, "multi spaces"),
    ("Hello, world! How are you?", {"words": 5, "unique": 5, "avg_len": 3.8}, "punctuation"),
    ("'quoted' (paren) ;semi: colon!", {"words": 4, "unique": 4, "avg_len": 5.0}, "mixed punct"),
]

ok = True
for text, expected, label in cases:
    try:
        got = summarize(text)
    except Exception as e:
        print(f"FAIL [{label}]: raised {type(e).__name__}: {e}")
        ok = False
        continue
    status = "ok" if got == expected else "FAIL"
    if got != expected:
        ok = False
    print(f"{status} [{label}]: got {got!r}, expected {expected!r}")

print("\nALL OK" if ok else "\nSOME FAILURES")
