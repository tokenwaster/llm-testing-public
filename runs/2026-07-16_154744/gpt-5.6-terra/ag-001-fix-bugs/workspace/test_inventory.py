import inventory

stock = {"apple": 2}
assert inventory.add_item(stock, "apple", 3) is stock
assert stock == {"apple": 5}
assert inventory.add_item(stock, "pear", 0) == {"apple": 5, "pear": 0}

try:
    inventory.add_item(stock, "bad", -1)
    raise AssertionError("negative additions must fail")
except ValueError:
    pass

assert inventory.remove_item(stock, "apple", 5) == {"pear": 0}
try:
    inventory.remove_item(stock, "missing", 1)
    raise AssertionError("unknown items must fail")
except KeyError:
    pass
try:
    inventory.remove_item(stock, "pear", 1)
    raise AssertionError("over-removal must fail")
except ValueError:
    pass
assert inventory.remove_item(stock, "pear", 0) == {}

assert inventory.total_value({"apple": 2, "unknown": 7}, {"apple": 1.25}) == 2.5
print("all tests passed")
