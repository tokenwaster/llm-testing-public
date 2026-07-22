"""Quick reproducer for textstats bugs."""
from textstats import summarize

cases = [
    "Hello world",                          # basic
    "Hello,  world!",                       # multiple whitespace + punct
    "Dog. dog DOG",                         # case + punct
    "  tabs\tand\nnewlines  ",              # whitespace kinds
    "... !! ()",                            # punctuation-only tokens
    "It's a test.",                         # apostrophe in token
    "(hello) [world] {foo}",                # bracket chars (not in spec PUNCT)
    "",                                     # empty
    "   ",                                  # only whitespace
]

for c in cases:
    try:
        r = summarize(c)
        print(repr(c), "->", r)
    except Exception as e:
        print(repr(c), "-> ERROR:", type(e).__name__, e)