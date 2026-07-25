"""Quick spec checks for inventory.py."""
from inventory import add_item, remove_item, total_value

# add_item accumulates
inv = {}
assert add_item(inv, "apples", 3) is inv
assert inv == {"apples": 3}
add_item(inv, "apples", 4)
assert inv == {"apples": 7}, inv
add_item(inv, "pears", 2)
assert inv == {"apples": 7, "pears": 2}, inv

# add_item rejects negative qty
try:
    add_item(inv, "apples", -1)
    raise AssertionError("expected ValueError")
except ValueError:
    pass

# remove_item: normal removal, exact-to-zero deletion
remove_item(inv, "apples", 5)
assert inv == {"apples": 2, "pears": 2}, inv
remove_item(inv, "pears", 2)
assert inv == {"apples": 2}, inv  # pears key deleted

# remove_item: unknown name -> KeyError
try:
    remove_item(inv, "bananas", 1)
    raise AssertionError("expected KeyError")
except KeyError:
    pass

# remove_item: removing more than available -> ValueError
try:
    remove_item(inv, "apples", 3)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
assert inv == {"apples": 2}, inv  # unchanged

# total_value: normal + missing price counts as 0
assert total_value({"apples": 2, "pears": 5}, {"apples": 1.5, "pears": 2.0}) == 13.0
assert total_value({"apples": 2, "pears": 5}, {"apples": 1.5}) == 3.0
assert total_value({}, {}) == 0
assert total_value({"apples": 2}, {}) == 0

print("All tests passed!")
