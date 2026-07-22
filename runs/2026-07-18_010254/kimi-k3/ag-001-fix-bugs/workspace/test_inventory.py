from inventory import add_item, remove_item, total_value

# add_item accumulates
inv = {}
assert add_item(inv, "apple", 3) is inv
assert add_item(inv, "apple", 2) == {"apple": 5}
assert add_item(inv, "pear", 1) == {"apple": 5, "pear": 1}
try:
    add_item(inv, "apple", -1)
    raise AssertionError("expected ValueError")
except ValueError:
    pass

# remove_item
remove_item(inv, "apple", 2)
assert inv == {"apple": 3, "pear": 1}
remove_item(inv, "apple", 3)  # exactly 0 -> key deleted
assert inv == {"pear": 1}
try:
    remove_item(inv, "banana", 1)
    raise AssertionError("expected KeyError")
except KeyError:
    pass
try:
    remove_item(inv, "pear", 5)
    raise AssertionError("expected ValueError")
except ValueError:
    pass

# total_value, missing prices count as 0
assert total_value({"pear": 2, "fig": 4}, {"pear": 1.5}) == 3.0
assert total_value({}, {}) == 0
assert total_value({"a": 2, "b": 3}, {"a": 2.0, "b": 1.0}) == 7.0

print("all tests passed")
