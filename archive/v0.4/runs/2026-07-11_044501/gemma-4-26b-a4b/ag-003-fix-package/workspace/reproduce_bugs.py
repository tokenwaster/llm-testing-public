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
            "input": "  multiple   spaces\t\nand\ttabs  ",
            "expected": {"words": 4, "unique": 4, "avg_len": 5.25}
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
            "input": "One, two; three! (four)",
            "expected": {"words": 4, "unique": 4, "avg_len": 3.75}
        },
        {
            "input": "Apple apple APPLE",
            "expected": {"words": 3, "unique": 1, "avg_len": 5.0}
        }
    ]

    for i, case in enumerate(test_cases):
        try:
            result = summarize(case["input"])
            if result != case["expected"]:
                print(f"Test case {i} failed: input='{case['input'].replace(chr(10), '[NL]')}', expected={case['expected']}, got={result}")
            else:
                print(f"Test case {i} passed")
        except Exception as e:
            print(f"Test case {i} raised exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_summarize()
