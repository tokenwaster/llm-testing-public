import textstats, json, sys

def test(txt):
    print(repr(txt), '->', textstats.summarize(txt))

samples = [
    "",
    "Hello world!",
    "Dog, cat dog. Cat!",
    "   Multiple   spaces\tand\nnewlines  ",
    "...!!!...",
]
for s in samples:
    test(s)
