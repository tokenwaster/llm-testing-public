"""Quick tests for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item accumulates
inv = {}
add_item(inv, "apple", 5)
assert inv["apple"] == 5, f"Expected 5, got {inv['apple']}"
add_item(inv, "apple", 3)
assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"

# Test add_item raises on negative qty
try:
    add_item(inv, "apple", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item
remove_item(inv, "apple", 8)
assert "apple" not in inv, "Key should be deleted when qty reaches 0"

# Test remove_item raises on unknown name
try:
    remove_item(inv, "banana", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item raises on over-removal
add_item(inv, "apple", 3)
try:
    remove_item(inv, "apple", 5)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value with missing prices counts as 0
inv2 = {"apple": 2, "banana": 3}
prices = {"apple": 1.5}
val = total_value(inv2, prices)
assert val == 3.0, f"Expected 3.0, got {val}"

print("All tests passed!")
