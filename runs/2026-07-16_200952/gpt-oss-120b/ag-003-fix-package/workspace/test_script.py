from textstats import summarize

def test(text):
    print('Input:', repr(text))
    print('Result:', summarize(text))

# Various cases
texts = [
    "",  # empty
    "   ",  # whitespace only
    "Hello world!",  # simple
    "Dog, dog. DOG!",  # case and punctuation
    "... !!!",  # only punctuation tokens
    "Multiple   spaces\tand\nnewlines",  # whitespace variations
    "'Quote' \"double\" (paren)"  # punctuation surrounding
]
for t in texts:
    test(t)
