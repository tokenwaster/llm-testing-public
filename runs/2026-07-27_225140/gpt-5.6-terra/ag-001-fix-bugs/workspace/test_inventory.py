import inventory

stock = {"apple": 3}
assert inventory.add_item(stock, "apple", 2) is stock
assert stock == {"apple": 5}
assert inventory.add_item(stock, "pear", 0) == {"apple": 5, "pear": 0}

try:
    inventory.add_item(stock, "bad", -1)
    raise AssertionError("negative additions must fail")
except ValueError:
    pass

assert inventory.remove_item(stock, "apple", 5) is stock
assert stock == {"pear": 0}
try:
    inventory.remove_item(stock, "missing", 1)
    raise AssertionError("unknown item must fail")
except KeyError:
    pass
try:
    inventory.remove_item(stock, "pear", 1)
    raise AssertionError("over-removal must fail")
except ValueError:
    pass

assert inventory.total_value({"pear": 2, "free": 4}, {"pear": 1.5}) == 3.0
print("all tests passed")
