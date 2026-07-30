from textstats import summarize
cases = {
    '': {'words': 0, 'unique': 0, 'avg_len': 0.0},
    'Dog dog.': {'words': 2, 'unique': 1, 'avg_len': 3.0},
    'a\tb\n c': {'words': 3, 'unique': 3, 'avg_len': 1.0},
    '!!! ...': {'words': 0, 'unique': 0, 'avg_len': 0.0},
    "Can't, DOG! dog": {'words': 3, 'unique': 2, 'avg_len': 3.67},
}
for text, expected in cases.items():
    actual = summarize(text)
    print(repr(text), actual)
    assert actual == expected
print('all checks passed')
