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
    raise AssertionError("negative add did not fail")

assert inventory.remove_item(stock, "apple", 2) is stock
assert stock["apple"] == 3
inventory.remove_item(stock, "apple", 3)
assert "apple" not in stock
try:
    inventory.remove_item(stock, "missing", 1)
except KeyError:
    pass
else:
    raise AssertionError("unknown removal did not fail")
try:
    inventory.remove_item(stock, "pear", 1)
except ValueError:
    pass
else:
    raise AssertionError("excess removal did not fail")

stock = {"apple": 2, "pear": 4}
assert inventory.total_value(stock, {"apple": 1.5}) == 3.0
assert isinstance(inventory.total_value({}, {}), float)
print("all tests passed")
