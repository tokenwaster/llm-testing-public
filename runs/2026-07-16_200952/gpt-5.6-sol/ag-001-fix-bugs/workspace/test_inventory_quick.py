import inventory

stock = {"apple": 2}
assert inventory.add_item(stock, "apple", 3) is stock
assert stock == {"apple": 5}
assert inventory.add_item(stock, "pear", 0) == {"apple": 5, "pear": 0}
try:
    inventory.add_item(stock, "apple", -1)
except ValueError:
    pass
else:
    raise AssertionError("negative add did not raise")

assert inventory.remove_item(stock, "apple", 2) is stock
assert stock["apple"] == 3
assert inventory.remove_item(stock, "apple", 3) == {"pear": 0}
try:
    inventory.remove_item(stock, "missing", 1)
except KeyError:
    pass
else:
    raise AssertionError("unknown removal did not raise")
try:
    inventory.remove_item(stock, "pear", 1)
except ValueError:
    pass
else:
    raise AssertionError("excess removal did not raise")

value = inventory.total_value({"apple": 3, "unknown": 10}, {"apple": 1.5})
assert value == 4.5
assert isinstance(value, float)
print("quick tests passed")
