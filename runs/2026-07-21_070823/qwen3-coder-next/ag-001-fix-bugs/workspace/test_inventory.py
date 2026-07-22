"""Test script for inventory module."""
from inventory import add_item, remove_item, total_value

# Test add_item - accumulation bug
print("Testing add_item...")
inventory = {}
add_item(inventory, "apple", 5)
assert inventory == {"apple": 5}, f"Expected {{'apple': 5}}, got {inventory}"

# Accumulation test - should add to existing quantity
add_item(inventory, "apple", 3)
assert inventory == {"apple": 8}, f"Expected {{'apple': 8}}, got {inventory}"
print("  Accumulation: PASS")

# Test remove_item
print("Testing remove_item...")
inventory = {"apple": 5}
remove_item(inventory, "apple", 2)
assert inventory == {"apple": 3}, f"Expected {{'apple': 3}}, got {inventory}"

# Remove to zero should delete key
remove_item(inventory, "apple", 3)
assert inventory == {}, f"Expected {{}}, got {inventory}"
print("  Remove to zero: PASS")

# Unknown name should raise KeyError
try:
    remove_item({}, "apple", 1)
    print("  KeyError test: FAIL (no exception)")
except KeyError:
    print("  KeyError test: PASS")

# Removing more than available should raise ValueError
try:
    inventory = {"apple": 2}
    remove_item(inventory, "apple", 5)
    print("  ValueError test: FAIL (no exception)")
except ValueError:
    print("  ValueError test: PASS")

# Test total_value - missing price should count as 0
print("Testing total_value...")
inventory = {"apple": 5, "banana": 3}
prices = {"apple": 2.0}  # banana is missing
result = total_value(inventory, prices)
assert result == 10.0, f"Expected 10.0 (5*2 + 3*0), got {result}"
print("  Missing price counts as 0: PASS")

# Test negative qty raises ValueError in add_item
print("Testing add_item with negative qty...")
try:
    add_item({}, "apple", -1)
    print("  Negative qty test: FAIL (no exception)")
except ValueError:
    print("  Negative qty test: PASS")

print("\nAll tests completed!")
