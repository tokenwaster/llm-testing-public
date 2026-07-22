"""Test script for inventory module."""
from inventory import add_item, remove_item, total_value

# Test add_item - accumulation
print("Testing add_item...")
inventory = {}
add_item(inventory, "apple", 5)
assert inventory == {"apple": 5}, f"Expected {{'apple': 5}}, got {inventory}"

# Accumulate more apples
add_item(inventory, "apple", 3)
assert inventory == {"apple": 8}, f"Expected {{'apple': 8}}, got {inventory}"
print("  add_item accumulation: PASS")

# Test ValueError for negative qty
try:
    add_item(inventory, "banana", -1)
    print("  add_item negative qty: FAIL (no exception)")
except ValueError:
    print("  add_item negative qty: PASS")

# Test remove_item - unknown name
print("\nTesting remove_item...")
inventory = {"apple": 5}
try:
    remove_item(inventory, "banana", 1)
    print("  remove_item unknown name: FAIL (no exception)")
except KeyError:
    print("  remove_item unknown name: PASS")

# Test ValueError for removing more than available
inventory = {"apple": 5}
try:
    remove_item(inventory, "apple", 10)
    print("  remove_item too much: FAIL (no exception)")
except ValueError:
    print("  remove_item too much: PASS")

# Test deletion when quantity reaches 0
inventory = {"apple": 5}
remove_item(inventory, "apple", 5)
assert inventory == {}, f"Expected {{}}, got {inventory}"
print("  remove_item delete zero: PASS")

# Test total_value - missing price
print("\nTesting total_value...")
inventory = {"apple": 5, "banana": 3}
prices = {"apple": 1.0, "orange": 2.0}  # banana is missing
result = total_value(inventory, prices)
expected = 5 * 1.0 + 3 * 0  # banana should count as 0
assert result == expected, f"Expected {expected}, got {result}"
print("  total_value missing price: PASS")

# Test normal case
inventory = {"apple": 5, "banana": 3}
prices = {"apple": 1.0, "banana": 2.0}
result = total_value(inventory, prices)
expected = 5 * 1.0 + 3 * 2.0
assert result == expected, f"Expected {expected}, got {result}"
print("  total_value normal: PASS")

print("\nAll tests completed!")
