import inventory

# Test add_item
inv = {}
inventory.add_item(inv, "apple", 5)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"
inventory.add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"
try:
    inventory.add_item(inv, "banana", -1)
    raise AssertionError("Expected ValueError for negative qty")
except ValueError:
    pass

# Test remove_item
inventory.remove_item(inv, "apple", 8)
assert "apple" not in inv, f"Key should be deleted when qty reaches 0, got {inv}"
inv["banana"] = 10
try:
    inventory.remove_item(inv, "banana", 15)
    raise AssertionError("Expected ValueError for removing too much")
except ValueError:
    pass
inv2 = {"banana": 10}
inventory.remove_item(inv2, "banana", 3)
assert inv2 == {"banana": 7}, f"Expected {{'banana': 7}}, got {inv2}"
try:
    inventory.remove_item(inv2, "unknown", 1)
    raise AssertionError("Expected KeyError for unknown name")
except KeyError:
    pass

# Test total_value
inv3 = {"apple": 2, "banana": 3}
prices = {"apple": 1.5, "banana": 2.0}
assert inventory.total_value(inv3, prices) == 9.0, f"Expected 9.0, got {inventory.total_value(inv3, prices)}"
prices_missing = {"apple": 1.5}
assert inventory.total_value(inv3, prices_missing) == 3.0, f"Expected 3.0, got {inventory.total_value(inv3, prices_missing)}"

print("All tests passed.")
