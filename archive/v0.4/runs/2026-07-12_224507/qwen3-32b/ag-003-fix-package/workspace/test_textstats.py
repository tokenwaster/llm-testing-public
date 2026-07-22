from textstats import summarize

assert summarize('') == {'words': 0, 'unique': 0, 'avg_len': 0.0}
assert summarize('  ') == {'words': 0, 'unique': 0, 'avg_len': 0.0}
assert summarize("Hello!\nhello") == {'words': 2, 'unique': 1, 'avg_len': 5.0}
assert summarize("Dog. dog (cat)") == {'words': 3, 'unique': 2, 'avg_len': 3.33}
assert summarize(":\'\"\') == {'words': 0, 'unique': 0, 'avg_len': 0.0}
print('All tests passed!')