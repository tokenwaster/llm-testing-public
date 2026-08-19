from textstats import summarize

def check(text, expected):
    got = summarize(text)
    print(repr(text), "->", got, "expected", expected)
    assert got == expected, (got, expected)

check("", {"words": 0, "unique": 0, "avg_len": 0.0})
check("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0})
check("hello", {"words": 1, "unique": 1, "avg_len": 5.0})
check("hello world", {"words": 2, "unique": 2, "avg_len": 5.0})
check("hello   world", {"words": 2, "unique": 2, "avg_len": 5.0})
check("hello\tworld\nfoo", {"words": 3, "unique": 3, "avg_len": 4.33})
check("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0})
check("...", {"words": 0, "unique": 0, "avg_len": 0.0})
check("Hello, world!", {"words": 2, "unique": 2, "avg_len": 5.0})
check("a b c", {"words": 3, "unique": 3, "avg_len": 1.0})
check("(hello)", {"words": 1, "unique": 1, "avg_len": 5.0})
check("It's", {"words": 1, "unique": 1, "avg_len": 4.0})
check("DOG dog Dog.", {"words": 3, "unique": 1, "avg_len": 3.0})
check("one; two: three!", {"words": 3, "unique": 3, "avg_len": 3.67})
check("  hello  ", {"words": 1, "unique": 1, "avg_len": 5.0})

print("all passed")
