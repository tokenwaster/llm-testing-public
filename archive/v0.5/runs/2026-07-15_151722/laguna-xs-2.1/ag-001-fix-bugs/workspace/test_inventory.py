"""Test script for inventory.py"""
import inventory

# Test add_item - should accumulate
print("Testing add_item...")
inv = {}
inventory.add_item(inv, "apples", 5)
print(f"After adding 5 apples: {inv}")
assert inv == {"apples": 5}, f"Expected {{'apples': 5}}, got {inv}"

inventory.add_item(inv, "apples", 3)
print(f"After adding 3 more apples: {inv}")
assert inv == {"apples": 8}, f"Expected {{'apples': 8}}, got {inv}"  # Should be 8, not 3

# Test add_item with negative qty
try:
    inventory.add_item(inv, "apples", -1)
    print("ERROR: Should have raised ValueError for negative qty")
except ValueError:
    print("Correctly raised ValueError for negative qty")

# Test remove_item
print("\nTesting remove_item...")
inv = {"apples": 10}
inventory.remove_item(inv, "apples", 3)
print(f"After removing 3 apples: {inv}")
assert inv == {"apples": 7}, f"Expected {{'apples': 7}}, got {inv}"

# Test remove_item - unknown name
try:
    inventory.remove_item(inv, "oranges", 1)
    print("ERROR: Should have raised KeyError for unknown name")
except KeyError:
    print("Correctly raised KeyError for unknown name")

# Test remove_item - more than available
try:
    inventory.remove_item(inv, "apples", 20)
    print("ERROR: Should have raised ValueError for removing more than available")
except ValueError:
    print("Correctly raised ValueError for removing more than available")

# Test remove_item - delete when reaches 0
inv = {"apples": 5}
inventory.remove_item(inv, "apples", 5)
print(f"After removing all apples: {inv}")
assert inv == {}, f"Expected {{}}, got {inv}"

# Test total_value
print("\nTesting total_value...")
inv = {"apples": 10, "oranges": 5}
prices = {"apples": 2.0}  # oranges missing from prices
value = inventory.total_value(inv, prices)
print(f"Total value: {value}")
# apples: 10 * 2.0 = 20, oranges: 5 * 0 = 0, total = 20
assert value == 20.0, f"Expected 20.0, got {value}"

print("\nAll tests passed!")