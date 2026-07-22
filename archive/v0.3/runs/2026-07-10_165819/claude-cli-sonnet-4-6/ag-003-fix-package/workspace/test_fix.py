from textstats import summarize

r = summarize('')
assert r == {'words': 0, 'unique': 0, 'avg_len': 0.0}, f'empty failed: {r}'

r = summarize('hello\tworld\n\nfoo')
assert r['words'] == 3, f'whitespace split failed: {r}'

r = summarize('Dog dog DOG')
assert r['unique'] == 1, f'case insensitive failed: {r}'

r = summarize('Hello, world! ...')
assert r['words'] == 2, f'punct strip failed: {r}'
assert r['unique'] == 2, f'punct unique failed: {r}'

r = summarize('Dog. dog')
assert r == {'words': 2, 'unique': 1, 'avg_len': 3.0}, f'dog. dog failed: {r}'

r = summarize('hi there')
assert r['avg_len'] == 3.5, f'avg_len failed: {r}'

print('All tests passed')
print(summarize('The quick brown fox.'))
