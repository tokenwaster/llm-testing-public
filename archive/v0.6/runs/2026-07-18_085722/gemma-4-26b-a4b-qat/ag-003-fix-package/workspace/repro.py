from textstats import summarize

def test_summarize():
    test_cases = [
        {
            "input": "Dog. dog",
            "expected": {"words": 2, "unique": 1, "avg_len": 3.0},
            "description": "Case-insensitive and punctuation stripping"
        },
        {
            "input": "Hello, world! Hello world.",
            "expected": {"words": 4, "unique": 2, "avg_len": 5.0},
            "description": "Multiple whitespaces and punctuation"
        },
        {
            "input": "   ",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0},
            "description": "Empty/whitespace input"
        },
        {
            "input": "!!! ???",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0},
            "description": "Only punctuation"
        },
        {
            "input": "Word\twith\nnewlines and\t\ttabs.",
            "expected": {"words": 5, "unique": 5, "avg_len": 4.2}, # "Word", "with", "newlines", "and", "tabs"
            # Wait, let's re-calculate avg_len for "Word with newlines and tabs"
            # "Word" (4), "with" (4), "newlines" (8), "and" (3), "tabs" (4)
            # Sum = 4+4+8+3+4 = 23. 23/5 = 4.6
            # Let's check the example again.
            "expected": {"words": 5, "unique": 5, "avg_len": 4.6},
            "description": "Tabs and newlines"
        },
        {
            "input": "A b C a B c",
            "expected": {"words": 6, "unique": 3, "avg_len": 1.0},
            "description": "Case insensitivity"
        }
    ]

    for case in test_cases:
        result = summarize(case["input"])
        if result != case["expected"]:
            print(f"FAILED: {case['description']}")
            print(f"  Input: {repr(case['input'])}")
            print(f"  Expected: {case['expected']}")
            print(f"  Got:      {result}")
        else:
            print(f"PASSED: {case['description']}")

if __name__ == "__main__":
    test_summarize()
