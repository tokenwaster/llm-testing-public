"""Quick checks against the spec."""
from inventory import add_item, remove_item, total_value

# add_item accumulates
inv = {}
add_item(inv, "apple", 3)
add_item(inv, "apple", 2)
assert inv == {"apple": 5}, inv
assert add_item(inv, "pear", 1) is inv  # returns the inventory

# add_item with negative qty raises ValueError
try:
    add_item(inv, "apple", -1)
except ValueError:
    pass
else:
    raise AssertionError("expected ValueError")

# remove_item: unknown name -> KeyError
try:
    remove_item(inv, "banana", 1)
except KeyError:
    pass
else:
    raise AssertionError("expected KeyError")

# remove_item: removing more than stock -> ValueError
try:
    remove_item(inv, "apple", 10)
except ValueError:
    pass
else:
    raise AssertionError("expected ValueError")

# remove_item: partial removal, then exact removal deletes the key
remove_item(inv, "apple", 2)
assert inv["apple"] == 3, inv
remove_item(inv, "apple", 3)
assert "apple" not in inv, inv

# total_value: missing prices count as 0
inv = {"apple": 5, "mystery": 10}
assert total_value(inv, {"apple": 2.0}) == 10.0
assert total_value({}, {}) == 0

print("All spec checks passed.")
