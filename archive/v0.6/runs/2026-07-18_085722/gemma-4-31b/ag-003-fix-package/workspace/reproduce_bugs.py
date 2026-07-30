from textstats import summarize

def test():
    tests = [
        {
            "name": "Basic",
            "text": "Hello world",
            "expected": {"words": 2, "unique": 2, "avg_len": 5.0}
        },
        {
            "name": "Whitespace",
            "text": " Hello   world\t\nnext ",
            "expected": {"words": 3, "unique": 3, "avg_len": 4.67} # (5+5+4)/3 = 14/3 = 4.666...
        },
        {
            "name": "Case and Punctuation",
            "text": "Dog. dog DOG!",
            "expected": {"words": 3, "unique": 1, "avg_len": 3.0}
        },
        {
            "name": "Only Punctuation",
            "text": "... !!! ???",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0}
        },
        {
            "name": "Empty String",
            "text": "",
            "expected": {"words": 0, "unique": 0, "avg_len": 0.0}
        },
        {
            "name": "Mixed Punctuation",
            "text": "(Hello), 'world'!",
            "expected": {"words": 2, "unique": 2, "avg_len": 5.0} # Hello(5), world(5) -> (5+5)/2 = 5.0
        },
    ]

    for t in tests:
        result = summarize(t["text"])
        if result == t["expected"]:
            print(f"PASS: {t['name']}")
        else:
            print(f"FAIL: {t['name']} | Expected {t['expected']}, got {result}")

if __name__ == "__main__":
    test()
