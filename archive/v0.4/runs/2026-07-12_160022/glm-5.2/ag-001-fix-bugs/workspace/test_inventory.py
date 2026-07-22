from inventory import add_item, remove_item, total_value

inv = {}

# add accumulates
add_item(inv, "a", 5)
add_item(inv, "a", 3)
assert inv == {"a": 8}, inv

# negative qty raises
try:
    add_item(inv, "a", -1)
    assert False
except ValueError:
    pass

# remove unknown raises KeyError
try:
    remove_item(inv, "z", 1)
    assert False
except KeyError:
    pass

# remove too much raises ValueError
try:
    remove_item(inv, "a", 100)
    assert False
except ValueError:
    pass

# remove to zero deletes key
remove_item(inv, "a", 8)
assert inv == {}, inv

# remove partial
add_item(inv, "b", 10)
remove_item(inv, "b", 4)
assert inv == {"b": 6}, inv

# total_value: missing price counts as 0
add_item(inv, "c", 2)
prices = {"b": 3}  # c missing
assert total_value(inv, prices) == 6 * 3, total_value(inv, prices)

print("All tests passed.")
