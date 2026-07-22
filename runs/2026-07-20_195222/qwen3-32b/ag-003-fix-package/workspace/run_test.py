from textstats import summarize

test_cases = [
    ('', {'words': 0, 'unique': 0, 'avg_len': 0.0}),
    ('   ', {'words': 0, 'unique': 0, 'avg_len': 0.0}),
    ('Hello!', {'words': 1, 'unique': 1, 'avg_len': 5.0}),
    ('dog Dog', {'words': 2, 'unique': 1, 'avg_len': 3.0}),
    ("\'Wow...\'", {'words': 1, 'unique': 1, 'avg_len': 3.0}),
]

for text, expected in test_cases:
    result = summarize(text)
    assert result == expected, f"\nText: {repr(text)}\nGot: {result}\nExpected: {expected}"
print('All tests passed!')