from textstats import summarize

test_cases = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("Hello! world.", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 4.0}),
    ("This is a test. This is only a test.", {"words": 8, "unique": 5, "avg_len": round((4+2+1+4+4)/8, 2)}),
    ("Punctuation: here!", {"words": 2, "unique": 2, "avg_len": (10 + 4)/2}),
    ("Mixed CASE case", {"words": 3, "unique": 2, "avg_len": (5+4+4)/3})
]

for i, (input_text, expected) in enumerate(test_cases):
    result = summarize(input_text)
    assert result == expected, f"Test {i} failed: {result} != {expected}"

print("All tests passed!")