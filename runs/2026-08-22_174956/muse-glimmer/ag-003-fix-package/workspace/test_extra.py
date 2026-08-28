from textstats import summarize

def check(text, expected):
    res = summarize(text)
    print(text, res, "OK" if res==expected else f"FAIL expected {expected}")

check("a a A", {"words":3,"unique":1,"avg_len":1.0})
check("Hello!!!", {"words":1,"unique":1,"avg_len":5.0})
check("  \t\n  ", {"words":0,"unique":0,"avg_len":0.0})
check("one two three", {"words":3,"unique":3,"avg_len":3.67}) # (3+3+5)/3=3.666...
check("!!! ... ,,,", {"words":0,"unique":0,"avg_len":0.0})
