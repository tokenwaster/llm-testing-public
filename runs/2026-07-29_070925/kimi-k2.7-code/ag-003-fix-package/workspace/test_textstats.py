from textstats import summarize

# Cases from spec
assert summarize("") == {"words": 0, "unique": 0, "avg_len": 0.0}
assert summarize("   \t\n  ") == {"words": 0, "unique": 0, "avg_len": 0.0}
assert summarize("Hello world") == {"words": 2, "unique": 2, "avg_len": 5.0}
assert summarize("Dog. dog dog!") == {"words": 3, "unique": 1, "avg_len": 3.0}
assert summarize("one, two\tthree\nfour") == {"words": 4, "unique": 4, "avg_len": 3.75}
assert summarize("... !!!") == {"words": 0, "unique": 0, "avg_len": 0.0}
assert summarize("A a A.") == {"words": 3, "unique": 1, "avg_len": 1.0}
assert summarize("(hello) 'world'") == {"words": 2, "unique": 2, "avg_len": 5.0}
print("all tests passed")
