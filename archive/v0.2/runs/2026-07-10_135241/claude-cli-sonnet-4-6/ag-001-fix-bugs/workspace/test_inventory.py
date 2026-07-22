from inventory import add_item, remove_item, total_value

inv = {}
add_item(inv, 'apple', 5)
add_item(inv, 'apple', 3)
assert inv == {'apple': 8}, f'accumulate failed: {inv}'

try:
    add_item(inv, 'apple', -1)
    assert False, 'should raise ValueError'
except ValueError:
    pass

try:
    remove_item({}, 'x', 1)
    assert False
except KeyError:
    pass

inv2 = {'apple': 3}
try:
    remove_item(inv2, 'apple', 5)
    assert False
except ValueError:
    pass

inv3 = {'apple': 3}
remove_item(inv3, 'apple', 3)
assert inv3 == {}, f'key not deleted: {inv3}'

inv4 = {'apple': 4, 'banana': 2}
prices = {'apple': 1.5}
val = total_value(inv4, prices)
assert val == 6.0, f'total_value wrong: {val}'

print('All tests passed.')
