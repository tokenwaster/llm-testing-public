from textstats import summarize

cases = [
    "Dog. dog",                 # case-insensitive unique
    "one\ttwo\nthree",         # arbitrary whitespace
    "... !!! ()",               # punctuation-only input
    "",                         # empty input
]

for text in cases:
    try:
        print(repr(text), "->", summarize(text))
    except Exception as exc:
        print(repr(text), "->", type(exc).__name__, exc)
