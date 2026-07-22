from textstats import summarize

def test_summarize():
    test_cases = [
        {
            "input": "Dog dog.",
            "expected": {"words": 2, "unique": 1, "avg_len": 3.0}
        },
        {
            "input": "Hello\tworld\nthis is   a test",
            "expected": {"words": 6, "unique": 6, "avg_len": 3.5} # hello(5), world(5), this(4), is(2), a(1), test(4) -> (21/6) = 3.5
        },
        {
            "input": "!!!",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0}
        },
        {
            "input": "",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0}
        },
        {
            "input": "  ",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0}
        },
        {
            "input": "Apple, banana; apple.",
            "expected": {"words": 3, "unique": 2, "avg_len": 5.33}
        }
    ]

    for i, case in enumerate(test_cases):
        try:
            result = summarize(case["input"])
            if result != case["expected"]:
                print(f"Test case {i} failed: input={repr(case['input'])}, expected={case['expected']}, got={result}")
            else:
                print(f"Test case {i} passed!")
        except Exception as e:
            print(f"Test case {i} raised exception: {e}")

if __name__ == "__main__":
    test_summarize()
