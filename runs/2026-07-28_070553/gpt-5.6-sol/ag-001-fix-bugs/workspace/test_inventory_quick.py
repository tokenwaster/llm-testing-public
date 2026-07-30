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
    raise AssertionError("negative add must fail")

try:
    inventory.remove_item(stock, "missing", 1)
except KeyError:
    pass
else:
    raise AssertionError("unknown removal must fail")

try:
    inventory.remove_item(stock, "apple", 6)
except ValueError:
    pass
else:
    raise AssertionError("excess removal must fail")

assert inventory.remove_item(stock, "apple", 5) is stock
assert "apple" not in stock
assert inventory.total_value({"pear": 4, "unknown": 10}, {"pear": 1.5}) == 6.0
print("quick tests passed")
