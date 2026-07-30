from textstats import summarize

def check(text, expected):
    got = summarize(text)
    assert got == expected, f"{text!r}: got {got}, expected {expected}"
    print(f"OK: {text!r} -> {got}")

check("", {"words": 0, "unique": 0, "avg_len": 0.0})
check("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0})
check("hello", {"words": 1, "unique": 1, "avg_len": 5.0})
check("Dog. dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0})
check("Hello, world!", {"words": 2, "unique": 2, "avg_len": 5.0})
check("a  b\tc\nd", {"words": 4, "unique": 4, "avg_len": 1.0})
check("...", {"words": 0, "unique": 0, "avg_len": 0.0})
check("Hi!!! bye?", {"words": 2, "unique": 2, "avg_len": 2.5})
check("(hello) 'world'", {"words": 2, "unique": 2, "avg_len": 5.0})
print("All passed")
