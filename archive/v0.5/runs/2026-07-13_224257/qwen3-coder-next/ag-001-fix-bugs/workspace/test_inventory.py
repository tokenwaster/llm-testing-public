"""Test script for inventory module."""
from inventory import add_item, remove_item, total_value

# Test add_item - accumulation bug
print("Testing add_item...")
inventory = {}
add_item(inventory, "apple", 5)
assert inventory == {"apple": 5}, f"Expected {{'apple': 5}}, got {inventory}"

# Accumulate instead of overwrite
add_item(inventory, "apple", 3)
assert inventory == {"apple": 8}, f"Expected {{'apple': 8}}, got {inventory}"
print("add_item accumulation: PASS")

# Test remove_item
print("\nTesting remove_item...")
inventory = {"apple": 5}
remove_item(inventory, "apple", 2)
assert inventory == {"apple": 3}, f"Expected {{'apple': 3}}, got {inventory}"

# Delete when reaches 0
remove_item(inventory, "apple", 3)
assert inventory == {}, f"Expected {{}}, got {inventory}"
print("remove_item: PASS")

# Test total_value - missing price should count as 0
print("\nTesting total_value...")
inventory = {"apple": 5, "banana": 3}
prices = {"apple": 1.5}
expected = 5 * 1.5 + 3 * 0  # banana has no price, counts as 0
result = total_value(inventory, prices)
assert result == expected, f"Expected {expected}, got {result}"
print("total_value missing price: PASS")

print("\nAll tests passed!")
