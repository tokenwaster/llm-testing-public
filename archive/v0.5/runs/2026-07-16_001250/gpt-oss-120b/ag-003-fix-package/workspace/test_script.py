import textstats, json, sys, traceback

def test(text, expected):
    result = textstats.summarize(text)
    print('Input:', repr(text))
    print('Result:', result)
    print('Expected:', expected)
    assert result == expected, f"Mismatch: {result} != {expected}"

# Cases
test('', {"words":0,"unique":0,"avg_len":0.0})
test('   ', {"words":0,"unique":0,"avg_len":0.0})
test('Hello', {"words":1,"unique":1,"avg_len":5.0})
test('Hello world', {"words":2,"unique":2,"avg_len":5.0})
test('Hello, world!', {"words":2,"unique":2,"avg_len":5.0})
test('Dog dog DOG.', {"words":3,"unique":1,"avg_len":3.0})
test('Wow!   Such   punctuation...\nNew\tline', {"words":4,"unique":4,"avg_len":4.0})
print('All tests passed')
