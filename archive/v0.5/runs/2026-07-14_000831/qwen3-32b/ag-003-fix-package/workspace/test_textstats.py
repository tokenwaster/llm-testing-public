from textstats import summarize

def test():
    assert summarize('') == {'words': 0, 'unique': 0, 'avg_len': 0.0}
    assert summarize('  ') == {'words': 0, 'unique': 0, 'avg_len': 0.0}

    # Basic case
    res = summarize('Dog dog.')
    assert res['words'] == 2
    assert res['unique'] == 1
    assert res['avg_len'] == 3.0

    # Punctuation and whitespace handling
    res = summarize('Hello!   hello, world?')
    assert res['words'] == 3
    assert res['unique'] == 2
    assert res['avg_len'] == (5 + 5 + 4)/3
    # Empty after cleaning
    res = summarize('!!!')
    assert res['words'] == 0

    print('All tests passed!')
test()