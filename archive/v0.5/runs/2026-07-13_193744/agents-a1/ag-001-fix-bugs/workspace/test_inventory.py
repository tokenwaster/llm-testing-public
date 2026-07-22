"""Test script for inventory module."""
from inventory import add_item, remove_item, total_value

# Test add_item - should accumulate
inv = {}
add_item(inv, "apple", 10)
print("After adding apple 10:", inv)
add_item(inv, "apple", 5)
print("After adding apple 5 more:", inv)
assert inv["apple"] == 15, f"Expected 15, got {inv['apple']}"

# Test add_item with negative qty
try:
    add_item(inv, "banana", -1)
    print("ERROR: Should have raised ValueError")
except ValueError as e:
    print(f"Correctly raised ValueError: {e}")

# Test remove_item
inv2 = {"apple": 10, "banana": 5}
remove_item(inv2, "apple", 3)
print("After removing apple 3:", inv2)
assert inv2["apple"] == 7

# Test remove_item with unknown name
try:
    remove_item(inv2, "orange", 1)
    print("ERROR: Should have raised KeyError")
except KeyError as e:
    print(f"Correctly raised KeyError: {e}")

# Test remove_item more than available
try:
    remove_item(inv2, "apple", 100)
    print("ERROR: Should have raised ValueError")
except ValueError as e:
    print(f"Correctly raised ValueError: {e}")

# Test total_value with missing prices
inv3 = {"apple": 10, "banana": 5}
prices = {"apple": 1.5}
value = total_value(inv3, prices)
print(f"Total value (banana missing from prices): {value}")
assert value == 15.0, f"Expected 15.0, got {value}"

# Test total_value normal case
prices2 = {"apple": 1.5, "banana": 2.0}
value2 = total_value(inv3, prices2)
print(f"Total value (all prices present): {value2}")
assert value2 == 25.0, f"Expected 25.0, got {value2}"

print("All tests passed!")
