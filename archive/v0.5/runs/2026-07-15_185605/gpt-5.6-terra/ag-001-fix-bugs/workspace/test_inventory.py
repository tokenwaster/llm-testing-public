import inventory

stock = {"apples": 3}
assert inventory.add_item(stock, "apples", 2) is stock
assert stock == {"apples": 5}
assert inventory.add_item(stock, "bananas", 0) == {"apples": 5, "bananas": 0}
try:
    inventory.add_item(stock, "bad", -1)
    raise AssertionError("negative additions must fail")
except ValueError:
    pass

assert inventory.remove_item(stock, "apples", 5) == {"bananas": 0}
try:
    inventory.remove_item(stock, "missing", 1)
    raise AssertionError("missing item must fail")
except KeyError:
    pass
try:
    inventory.remove_item(stock, "bananas", 1)
    raise AssertionError("oversell must fail")
except ValueError:
    pass

assert inventory.total_value({"a": 2, "b": 4}, {"a": 1.5}) == 3.0
print("all tests passed")
