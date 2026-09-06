from textstats import summarize

def check(name, text, expected):
    try:
        result = summarize(text)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} {name}: got {result}, expected {expected}")
    except Exception as e:
        print(f"ERROR {name}: raised {type(e).__name__}: {e} (expected {expected})")

# basic
check("basic", "hello world", {"words": 2, "unique": 2, "avg_len": 5.0})
# whitespace: tabs, newlines, multiple spaces
check("whitespace", "hello\tworld\nfoo  bar", {"words": 4, "unique": 4, "avg_len": 3.75})
# case-insensitive + punctuation
check("case-punct", 'Dog. dog "DOG,"', {"words": 3, "unique": 1, "avg_len": 3.0})
# punctuation-only tokens ignored
check("punct-only", "hello ... world ,,,", {"words": 2, "unique": 2, "avg_len": 5.0})
# empty
check("empty", "", {"words": 0, "unique": 0, "avg_len": 0.0})
check("spaces-only", "   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0})
check("punct-only-input", "... ,,, !!!", {"words": 0, "unique": 0, "avg_len": 0.0})
# avg_len rounding
check("avg", "a bb ccc", {"words": 3, "unique": 3, "avg_len": 2.0})
