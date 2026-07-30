
from textstats import summarize

def test():
    tests = [
        {
            "name": "Basic functionality",
            "text": "Hello world! Hello world.",
            "expected": {"words": 4, "unique": 2, "avg_len": 5.0}
        },
        {
            "name": "Case insensitivity",
            "text": "Dog dog DOG",
            "expected": {"words": 3, "unique": 1, "avg_len": 3.0}
        },
        {
            "name": "Various whitespace",
            "text": "Hello\tworld\n  this is a test",
            "expected": {"words": 6, "unique": 6, "avg_len": 3.5}
        },
        {
            "name": "Punctuation only",
            "text": "... !!! ???",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0}
        },
        {
            "name": "Empty string",
            "text": "",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0}
        },
        {
            "name": "Complex punctuation and case",
            "text": '"Dog." dog, DOG!',
            "expected": {"words": 3, "unique": 1, "avg_len": 3.0}
        }
    ]

    for t in tests:
        try:
            result = summarize(t["text"])
            if result == t['expected']:
                print(f"Test {t['name']}: PASS")
            else:
                print(f"Test {t['name']}: FAIL")
                print(f"  Expected: {t['expected']}")
                print(f"  Got:      {result}")
        except Exception as e:
            print(f"Test {t['name']}: ERROR ({type(e).__name__}: {e})")

if __name__ == "__main__":
    test()
