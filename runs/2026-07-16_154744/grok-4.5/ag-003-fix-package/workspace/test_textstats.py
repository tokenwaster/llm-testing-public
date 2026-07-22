from textstats import summarize

def check(name, text, expected):
    result = summarize(text)
    ok = result == expected
    print(f"{'OK' if ok else 'FAIL'}: {name}")
    if not ok:
        print(f"  got:      {result}")
        print(f"  expected: {expected}")

check("empty", "", {"words": 0, "unique": 0, "avg_len": 0.0})
check("whitespace only", "  \n\t  ", {"words": 0, "unique": 0, "avg_len": 0.0})
check("simple", "hello world", {"words": 2, "unique": 2, "avg_len": 5.0})
check("multi whitespace", "hello   world\tfoo\nbar", {"words": 4, "unique": 4, "avg_len": 4.0})
check("case insensitive", "Dog dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0})
check("punctuation", "Dog. dog, 'cat'", {"words": 3, "unique": 2, "avg_len": 3.0})
check("only punct", "... !!!", {"words": 0, "unique": 0, "avg_len": 0.0})
check("mixed", "Hello, world! Hello.", {"words": 3, "unique": 2, "avg_len": 5.0})
check("parens quotes", '(hello) "world"', {"words": 2, "unique": 2, "avg_len": 5.0})
check("leading trailing space", "  a b  ", {"words": 2, "unique": 2, "avg_len": 1.0})
check("avg rounding", "ab abc", {"words": 2, "unique": 2, "avg_len": 2.5})
check("inner punct kept", "don't", {"words": 1, "unique": 1, "avg_len": 5.0})
