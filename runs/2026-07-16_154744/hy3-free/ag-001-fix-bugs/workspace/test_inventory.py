from inventory import add_item, remove_item, total_value

# add_item accumulates
inv = {}
add_item(inv, "a", 3)
add_item(inv, "a", 2)
assert inv == {"a": 5}, inv

# add_item negative
try:
    add_item({}, "a", -1)
    assert False
except ValueError:
    pass

# remove_item
inv = {"a": 5}
remove_item(inv, "a", 2)
assert inv == {"a": 3}, inv

# remove to zero deletes key
remove_item(inv, "a", 3)
assert inv == {}, inv

# remove unknown
try:
    remove_item({}, "x", 1)
    assert False
except KeyError:
    pass

# remove too many
try:
    remove_item({"a": 1}, "a", 2)
    assert False
except ValueError:
    pass

# total_value missing price counts as 0
inv = {"a": 2, "b": 3}
prices = {"a": 10}
assert total_value(inv, prices) == 20, total_value(inv, prices)

print("All tests passed")
