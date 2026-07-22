from inventory import add_item, remove_item, total_value

inv = {}
add_item(inv, 'apple', 5)
add_item(inv, 'apple', 3)
assert inv == {'apple': 8}, inv

try:
    add_item(inv, 'apple', -1)
    raise AssertionError('should raise')
except ValueError:
    pass

try:
    remove_item({}, 'banana', 1)
    raise AssertionError('should raise')
except KeyError:
    pass

try:
    remove_item({'apple': 2}, 'apple', 5)
    raise AssertionError('should raise')
except ValueError:
    pass

inv2 = {'apple': 3}
remove_item(inv2, 'apple', 3)
assert inv2 == {}, inv2

inv3 = {'apple': 4, 'banana': 2}
prices = {'apple': 1.5}
assert total_value(inv3, prices) == 6.0, total_value(inv3, prices)

print('All tests passed.')
