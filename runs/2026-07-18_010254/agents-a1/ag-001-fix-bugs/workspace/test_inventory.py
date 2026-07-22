"""Test script for inventory module."""
from inventory import add_item, remove_item, total_value

# Test add_item accumulation
inv = {}
add_item(inv, "apple", 10)
print("After adding apple 10:", inv)
add_item(inv, "apple", 5)
print("After adding apple 5 more:", inv)
assert inv["apple"] == 15, f"Expected 15, got {inv.get('apple')}"

# Test add_item with negative qty
try:
    add_item(inv, "banana", -1)
    print("ERROR: Should have raised ValueError for negative qty")
except ValueError as e:
    print(f"Correctly raised ValueError: {e}")

# Test remove_item
inv2 = {"apple": 10, "banana": 5}
remove_item(inv2, "apple", 3)
print("After removing 3 apples:", inv2)
assert inv2["apple"] == 7

# Test remove_item more than available
try:
    remove_item(inv2, "banana", 10)
    print("ERROR: Should have raised ValueError for over-removal")
except ValueError as e:
    print(f"Correctly raised ValueError: {e}")

# Test remove_item unknown name
try:
    remove_item(inv2, "orange", 1)
    print("ERROR: Should have raised KeyError for unknown name")
except KeyError as e:
    print(f"Correctly raised KeyError: {e}")

# Test remove_item deletes at zero
inv3 = {"apple": 5}
remove_item(inv3, "apple", 5)
print("After removing all apples:", inv3)
assert "apple" not in inv3

# Test total_value with missing prices
inv4 = {"apple": 10, "banana": 5}
prices = {"apple": 1.5}
val = total_value(inv4, prices)
print(f"Total value: {val}")
assert val == 15.0, f"Expected 15.0, got {val}"

# Test total_value with all prices
prices2 = {"apple": 1.5, "banana": 2.0}
val2 = total_value(inv4, prices2)
print(f"Total value with all prices: {val2}")
assert val2 == 25.0, f"Expected 25.0, got {val2}"

print("\nAll tests passed!")
