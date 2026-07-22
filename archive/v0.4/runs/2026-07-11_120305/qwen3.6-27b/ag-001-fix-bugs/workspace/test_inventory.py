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
inv2 = {"banana": 10}
remove_item(inv2, "banana", 3)
assert inv2["banana"] == 7, f"Expected 7, got {inv2['banana']}"

# Test remove_item deletes key at 0
remove_item(inv2, "banana", 7)
assert "banana" not in inv2, "Key should be deleted"

# Test remove_item raises on unknown name
try:
    remove_item(inv2, "mango", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item raises on over-removal
inv3 = {"cherry": 2}
try:
    remove_item(inv3, "cherry", 5)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value with missing prices defaults to 0
inv4 = {"apple": 3, "banana": 2}
prices = {"apple": 1.5}  # banana missing
val = total_value(inv4, prices)
assert val == 4.5, f"Expected 4.5, got {val}"

print("All tests passed!")
