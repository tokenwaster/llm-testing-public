from textstats import summarize

# Final verification with correct expected values
tests = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("Dog. dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("hello\tworld\nfoo  bar", {"words": 4, "unique": 4, "avg_len": 4.0}),
    ("!!! ... ,,, hello", {"words": 1, "unique": 1, "avg_len": 5.0}),
    ("Hello, world!", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("'quoted' words", {"words": 2, "unique": 2, "avg_len": 5.5}),
    ("a b c d e f g h i j", {"words": 10, "unique": 10, "avg_len": 1.0}),
    ("  spaces   everywhere  ", {"words": 2, "unique": 2, "avg_len": 8.0}),  # (6+10)/2=8
    ("(parentheses) test", {"words": 2, "unique": 2, "avg_len": 7.5}),  # (11+4)/2=7.5
    ("only punctuation: !!!", {"words": 2, "unique": 2, "avg_len": 7.5}),  # only(4)+punctuation(11)=15/2=7.5
    ("!!!", {"words": 0, "unique": 0, "avg_len": 0.0}),  # punctuation only
    ("... ...", {"words": 0, "unique": 0, "avg_len": 0.0}),  # punctuation only
    ("a", {"words": 1, "unique": 1, "avg_len": 1.0}),
    ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}),  # whitespace only
]

all_pass = True
for text, expected in tests:
    result = summarize(text)
    if result != expected:
        print(f"FAIL: input={repr(text)}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        all_pass = False
    else:
        print(f"PASS: {repr(text)} -> {result}")

print(f"\n{'All tests passed!' if all_pass else 'Some tests FAILED!'}")
