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
remove_item(inv, "apple", 8)
assert "apple" not in inv, "apple should be deleted when qty reaches 0"

# Test remove_item KeyError
try:
    remove_item(inv, "banana", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item ValueError (too much)
add_item(inv, "apple", 5)
try:
    remove_item(inv, "apple", 10)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value with missing prices
inv = {"apple": 3, "banana": 2}
prices = {"apple": 1.0}
val = total_value(inv, prices)
assert val == 3.0, f"Expected 3.0, got {val}"

print("All tests passed!")
