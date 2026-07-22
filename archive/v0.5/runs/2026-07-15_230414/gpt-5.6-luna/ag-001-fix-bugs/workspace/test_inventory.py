from inventory import add_item, remove_item, total_value

inv = {}
assert add_item(inv, 'a', 2) is inv
assert add_item(inv, 'a', 3) == {'a': 5}
assert add_item(inv, 'b', 0) == {'a': 5, 'b': 0}
try:
    add_item(inv, 'a', -1)
except ValueError:
    pass
else:
    raise AssertionError
assert remove_item(inv, 'a', 5) == {'b': 0}
try:
    remove_item(inv, 'missing', 1)
except KeyError:
    pass
else:
    raise AssertionError
try:
    remove_item(inv, 'b', 1)
except ValueError:
    pass
else:
    raise AssertionError
assert total_value({'a': 2, 'b': 3}, {'a': 4}) == 8
print('ok')
