from textstats import summarize

cases = [
    "",                                  # empty
    "   ",                               # only whitespace
    "Dog. dog DOG cat",                  # case-insensitive uniqueness + punct
    "Hello\tworld\nfoo   bar",           # various whitespace
    "... !?! ()",                        # only punctuation -> no words
    "The quick brown fox.",              # trailing punctuation
]

for c in cases:
    print(repr(c), "->", summarize(c))
