from textstats import summarize

def test_summarize():
    test_cases = [
        {
            "input": "Dog. dog",
            "expected": {"words": 2, "unique": 1, "avg_len": 3.0},
            "desc": "Case-insensitive and punctuation stripping"
        },
        {
            "input": "Hello, world! Hello.",
            "expected": {"words": 3, "unique": 2, "avg_len": 5.0},
            "desc": "Punctuation and case-insensitivity"
        },
        {
            "input": "   ",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0},
            "desc": "Empty/whitespace input"
        },
        {
            "input": "!!! ???",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0},
            "desc": "Only punctuation"
        },
        {
            "input": "Word\twith\nmultiple\r\nspaces",
            "expected": {"words": 4, "unique": 4, "avg_len": 5.5},
            "desc": "Whitespace handling (tabs, newlines)"
        },
        {
            "input": "Multiple   spaces",
            "expected": {"words": 2, "unique": 2, "avg_len": 7.0},
            "desc": "Multiple spaces"
        },
    ]

    for i, tc in enumerate(test_cases):
        try:
            result = summarize(tc["input"])
            if result != tc["expected"]:
                print(f"FAILED test {i}: {tc['desc']}")
                print(f"  Input: {repr(tc['input'])}")
                print(f"  Expected: {tc['expected']}")
                print(f"  Got:      {result}")
            else:
                print(f"PASSED test {i}: {tc['desc']}")
        except Exception as e:
            print(f"ERROR test {i}: {tc['desc']} - {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_summarize()
