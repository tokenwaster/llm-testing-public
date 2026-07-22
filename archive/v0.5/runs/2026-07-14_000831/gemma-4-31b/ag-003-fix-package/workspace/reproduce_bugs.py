from textstats import summarize

def test():
    test_cases = [
        {
            "text": "Hello world",
            "expected": {"words": 2, "unique": 2, "avg_len": 5.0}
        },
        {
            "text": "Hello hello",
            "expected": {"words": 2, "unique": 1, "avg_len": 5.0}
        },
        {
            "text": "Dog. dog!",
            "expected": {"words": 2, "unique": 1, "avg_len": 3.0}
        },
        {
            "text": "  Multiple   spaces\tand\nnewlines  ",
            "expected": {"words": 4, "unique": 4, "avg_len": 6.25} # Multiple(8), spaces(6), and(3), newlines(8) -> (8+6+3+8)/4 = 25/4 = 6.25
        },
        {
            "text": "... !!!",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0}
        },
        {
            "text": "",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0}
        },
    ]

    for i, case in enumerate(test_cases):
        result = summarize(case["text"])
        if result == case["expected"]:
            print(f"Test {i} passed")
        else:
            print(f"Test {i} failed: expected {case['expected']}, got {result}")

if __name__ == "__main__":
    test()
