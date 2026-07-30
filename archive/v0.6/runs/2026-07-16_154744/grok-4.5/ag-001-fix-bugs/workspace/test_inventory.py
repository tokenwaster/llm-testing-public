"""Quick tests for inventory module."""
from inventory import add_item, remove_item, total_value

# add_item accumulates
inv = {}
add_item(inv, "apple", 3)
add_item(inv, "apple", 2)
assert inv == {"apple": 5}, inv

# add_item rejects negative
try:
    add_item(inv, "apple", -1)
    assert False, "should have raised"
except ValueError:
    pass

# remove_item
remove_item(inv, "apple", 2)
assert inv == {"apple": 3}, inv
remove_item(inv, "apple", 3)
assert inv == {}, inv

# remove unknown
try:
    remove_item(inv, "banana", 1)
    assert False, "should have raised"
except KeyError:
    pass

# remove too many
add_item(inv, "pear", 1)
try:
    remove_item(inv, "pear", 2)
    assert False, "should have raised"
except ValueError:
    pass

# total_value missing prices count as 0
inv = {"a": 2, "b": 3}
prices = {"a": 1.5}
assert total_value(inv, prices) == 3.0

print("all tests passed")
