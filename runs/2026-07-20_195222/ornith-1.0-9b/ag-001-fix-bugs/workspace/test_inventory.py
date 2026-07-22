from inventory import add_item, remove_item, total_value

# Test add_item: accumulates with existing quantity
inv = {}
add_item(inv, 'a', 5)
assert inv == {'a': 5}, f"Expected {{'a': 5}}, got {inv}"
add_item(inv, 'a', 3)
assert inv == {'a': 8}, f"Expected {{'a': 8}}, got {inv}"

# Test add_item: qty < 0 raises ValueError
try:
    add_item({}, 'x', -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item: removes quantity
inv = {'a': 8}
remove_item(inv, 'a', 2)
assert inv == {'a': 6}, f"Expected {{'a': 6}}, got {inv}"

# Test remove_item: reaches exactly 0 deletes key
inv = {'a': 3}
remove_item(inv, 'a', 3)
assert 'a' not in inv, f"Key should be deleted, got {inv}"

# Test remove_item: unknown name raises KeyError
try:
    remove_item({}, 'x', 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item: removing more than available raises ValueError
try:
    remove_item({'a': 3}, 'a', 5)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value: sums quantity * price
inv = {'a': 2, 'b': 3}
prices = {'a': 10.0, 'b': 5.0}
assert total_value(inv, prices) == 35.0, f"Expected 35.0, got {total_value(inv, prices)}"

# Test total_value: missing items count as 0
inv = {'a': 2, 'c': 4}
prices = {'a': 10.0}
assert total_value(inv, prices) == 20.0, f"Expected 20.0, got {total_value(inv, prices)}"

print("All tests passed!")
