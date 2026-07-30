from inventory import add_item, remove_item, total_value

inv = {}
assert add_item(inv, 'apple', 2) is inv
assert add_item(inv, 'apple', 3) == {'apple': 5}
try:
    add_item(inv, 'apple', -1)
except ValueError:
    pass
else:
    raise AssertionError
assert remove_item(inv, 'apple', 5) == {}
try:
    remove_item(inv, 'missing', 1)
except KeyError:
    pass
else:
    raise AssertionError
assert total_value({'a': 2, 'b': 3}, {'a': 1.5}) == 3.0
print('ok')
