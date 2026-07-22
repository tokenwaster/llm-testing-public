"""Quick tests for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item accumulation
inv = {}
add_item(inv, "apple", 5)
assert inv["apple"] == 5, f"Expected 5, got {inv['apple']}"
add_item(inv, "apple", 3)
assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"

# Test add_item ValueError
try:
    add_item(inv, "apple", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item
inv2 = {"banana": 10}
remove_item(inv2, "banana", 10)
assert "banana" not in inv2, "Key should be deleted when qty reaches 0"

# Test remove_item KeyError
try:
    remove_item({}, "missing", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item ValueError
try:
    remove_item({"x": 2}, "x", 5)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value with missing prices
inv3 = {"apple": 2, "banana": 3}
prices = {"apple": 1.5}  # banana missing
val = total_value(inv3, prices)
assert val == 3.0, f"Expected 3.0, got {val}"

print("All tests passed!")
