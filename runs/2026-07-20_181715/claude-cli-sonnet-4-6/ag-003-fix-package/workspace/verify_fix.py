import sys
sys.path.insert(0, '.')
from textstats import summarize

r = summarize('hello\tworld\n foo')
assert r == {'words': 3, 'unique': 3, 'avg_len': 4.33}, r

r = summarize('Dog. dog DOG')
assert r == {'words': 3, 'unique': 1, 'avg_len': 3.0}, r

r = summarize('hello ... world')
assert r == {'words': 2, 'unique': 2, 'avg_len': 5.0}, r

r = summarize('')
assert r == {'words': 0, 'unique': 0, 'avg_len': 0.0}, r

print('All assertions passed.')
