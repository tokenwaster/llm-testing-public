from inventory import add_item, remove_item, total_value

inv = {}

# add_item basic + accumulation
inv = add_item(inv, "apple", 3)
inv = add_item(inv, "apple", 2)
assert inv == {"apple": 5}, f"expected {{'apple': 5}}, got {inv}"

# add_item negative qty raises ValueError
try:
    add_item(inv, "apple", -1)
    assert False, "should have raised ValueError"
except ValueError:
    pass

# remove_item basic
inv = remove_item(inv, "apple", 2)
assert inv == {"apple": 3}, f"expected {{'apple': 3}}, got {inv}"

# remove_item deleting at 0
inv = remove_item(inv, "apple", 3)
assert inv == {}, f"expected {{}}, got {inv}"

# remove_item unknown raises KeyError
try:
    remove_item(inv, "banana", 1)
    assert False, "should have raised KeyError"
except KeyError:
    pass

# remove_item too many raises ValueError
inv = add_item({}, "pear", 2)
try:
    remove_item(inv, "pear", 5)
    assert False, "should have raised ValueError"
except ValueError:
    pass

# total_value with missing price
inv = {"apple": 4, "pear": 2}
prices = {"apple": 1.5}
assert total_value(inv, prices) == 4 * 1.5 + 0, f"got {total_value(inv, prices)}"

# total_value with all prices
inv = {"apple": 4, "pear": 2}
prices = {"apple": 1.5, "pear": 2.0}
assert total_value(inv, prices) == 4 * 1.5 + 2 * 2.0

# total_value empty
assert total_value({}, {"apple": 1.0}) == 0.0

print("All tests passed!")
