from textstats import summarize

r = summarize('hello world')
assert r == {'words': 2, 'unique': 2, 'avg_len': 5.0}, r

r = summarize('hello\tworld\nfoo')
assert r == {'words': 3, 'unique': 3, 'avg_len': round((5+5+3)/3, 2)}, r

r = summarize('a  b   c')
assert r == {'words': 3, 'unique': 3, 'avg_len': 1.0}, r

r = summarize('Dog dog DOG')
assert r['unique'] == 1, r

r = summarize('Dog. dog')
assert r['unique'] == 1, r
assert r['words'] == 2, r

r = summarize('hello ... world')
assert r['words'] == 2, r
assert r['unique'] == 2, r

r = summarize('"hello"')
assert r['avg_len'] == 5.0, r

r = summarize('')
assert r == {'words': 0, 'unique': 0, 'avg_len': 0.0}, r

r = summarize('...')
assert r == {'words': 0, 'unique': 0, 'avg_len': 0.0}, r

print('All assertions passed.')
