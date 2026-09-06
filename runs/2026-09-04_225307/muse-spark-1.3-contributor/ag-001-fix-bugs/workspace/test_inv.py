import inventory

# add_item accumulating
inv = {}
inventory.add_item(inv, "apple", 5)
inventory.add_item(inv, "apple", 3)
assert inv["apple"] == 8, inv
print("add accumulate ok")

# add negative raises
try:
    inventory.add_item({}, "a", -1)
    raise AssertionError("should have raised ValueError")
except ValueError:
    print("add negative ok")

# remove
inv = {"apple": 5}
inventory.remove_item(inv, "apple", 2)
assert inv["apple"] == 3, inv
print("remove partial ok")

# remove to zero deletes
inv = {"apple": 5}
inventory.remove_item(inv, "apple", 5)
assert "apple" not in inv, inv
print("remove to zero ok")

# remove unknown KeyError
try:
    inventory.remove_item({}, "nope", 1)
    raise AssertionError("should have raised KeyError")
except KeyError:
    print("remove unknown ok")

# remove too many ValueError
try:
    inventory.remove_item({"a": 2}, "a", 5)
    raise AssertionError("should have raised ValueError")
except ValueError:
    print("remove too many ok")

# total_value
assert inventory.total_value({"a": 2, "b": 3}, {"a": 10, "b": 5}) == 35
print("total basic ok")
assert inventory.total_value({"a": 2, "missing": 3}, {"a": 10}) == 20
print("total missing price ok")
assert isinstance(inventory.total_value({}, {}), float)
print("total float ok")

print("ALL PASS")
