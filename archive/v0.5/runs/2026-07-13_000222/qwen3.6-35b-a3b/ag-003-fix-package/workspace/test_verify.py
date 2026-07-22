from textstats import summarize

# Verify all edge cases
tests = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("hello", {"words": 1, "unique": 1, "avg_len": 5.0}),
    ("hello\tworld\nfoo", {"words": 3, "unique": 3, "avg_len": 4.33}),
    ("Dog. cat, DOG", {"words": 3, "unique": 2, "avg_len": 3.0}),
    ("... ,,, !!!", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("  hello   world  ", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("'Hello' \"World\" (Foo)", {"words": 3, "unique": 3, "avg_len": 5.0}),
    ("a b c a b", {"words": 5, "unique": 3, "avg_len": 1.0}),
    ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}),
]

all_pass = True
for text, expected in tests:
    result = summarize(text)
    status = "PASS" if result == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"{status}: {repr(text)} -> {result} (expected {expected})")

print(f"\n{'All tests passed!' if all_pass else 'Some tests FAILED!'}")
