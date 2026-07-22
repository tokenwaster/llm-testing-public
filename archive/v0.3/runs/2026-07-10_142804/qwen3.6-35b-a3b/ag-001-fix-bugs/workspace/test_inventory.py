"""Test script for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item
inv = {}
result = add_item(inv, "apple", 10)
assert inv == {"apple": 10}, f"Expected {{'apple': 10}}, got {inv}"

# Accumulation test
add_item(inv, "apple", 5)
assert inv == {"apple": 15}, f"Expected {{'apple': 15}}, got {inv}"

# Negative qty should raise ValueError
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item
inv2 = {"apple": 10, "banana": 5}
result = remove_item(inv2, "apple", 3)
assert inv2 == {"apple": 7, "banana": 5}, f"Got {inv2}"

# Remove all should delete key
remove_item(inv2, "banana", 5)
assert "banana" not in inv2, f"banana should be deleted, got {inv2}"

# Unknown name should raise KeyError
try:
    remove_item(inv2, "cherry", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Remove more than available should raise ValueError
inv3 = {"apple": 5}
try:
    remove_item(inv3, "apple", 10)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value
inv4 = {"apple": 10, "banana": 5}
prices = {"apple": 1.5, "banana": 2.0}
val = total_value(inv4, prices)
assert val == 10 * 1.5 + 5 * 2.0, f"Expected 25.0, got {val}"

# Items missing from prices should count as 0
prices2 = {"apple": 1.5}
val2 = total_value(inv4, prices2)
assert val2 == 10 * 1.5 + 5 * 0, f"Expected 15.0, got {val2}"

print("All tests passed!")
