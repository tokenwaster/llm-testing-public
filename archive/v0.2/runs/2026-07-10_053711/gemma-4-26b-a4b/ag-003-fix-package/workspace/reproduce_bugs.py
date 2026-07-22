from textstats import summarize

def test_summarize():
    test_cases = [
        {
            "input": "Hello world",
            "expected": {"words": 2, "unique": 2, "avg_len": 5.0}
        },
        {
            "input": "Dog. dog",
            "expected": {"words": 2, "unique": 1, "avg_len": 3.0}
        },
        {
            "input": "  multiple   spaces\t\nnewlines  ",
            "expected": {"words": 3, "unique": 3, "avg_len": 7.33}
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
            "input": "One, two; three!",
            "expected": {"words": 3, "unique": 3, "avg_len": 3.67}
        }
    ]

    for i, case in enumerate(test_cases):
        try:
            result = summarize(case["input"])
            if result == case["expected"]:
                print(f"Test case {i} passed!")
            else:
                print(f"Test case {i} failed! Input: {repr(case['input'])}, Expected: {case['expected']}, Got: {result}")
        except Exception as e:
            print(f"Test case {i} raised exception: {e}")

if __name__ == "__main__":
    test_summarize()
