#!/usr/bin/env python3
"""Test script for inventory module."""

from inventory import add_item, remove_item, total_value

# Test add_item accumulation
print("Testing add_item...")
inv = {}
add_item(inv, "apple", 10)
add_item(inv, "apple", 5)  # Should accumulate to 15
print(f"After adding apple twice: {inv}")
assert inv == {"apple": 15}, f"Expected {{'apple': 15}}, got {inv}"

# Test add_item with negative qty
try:
    add_item(inv, "banana", -5)
    print("ERROR: Should have raised ValueError for negative qty")
except ValueError as e:
    print(f"Correctly raised ValueError: {e}")

# Test remove_item
print("\nTesting remove_item...")
inv = {"apple": 10, "banana": 5}
remove_item(inv, "apple", 3)
print(f"After removing 3 apples: {inv}")
assert inv == {"apple": 7, "banana": 5}, f"Expected {{'apple': 7, 'banana': 5}}, got {inv}"

# Test remove_item with unknown name
try:
    remove_item(inv, "orange", 2)
    print("ERROR: Should have raised KeyError for unknown item")
except KeyError as e:
    print(f"Correctly raised KeyError: {e}")

# Test remove_item with insufficient stock
try:
    remove_item(inv, "apple", 10)
    print("ERROR: Should have raised ValueError for insufficient stock")
except ValueError as e:
    print(f"Correctly raised ValueError: {e}")

# Test removing to exactly 0
remove_item(inv, "banana", 5)
print(f"After removing all bananas: {inv}")
assert "banana" not in inv, f"Expected banana to be removed from inventory"

# Test total_value with missing prices
print("\nTesting total_value...")
inv = {"apple": 10, "banana": 5, "orange": 3}
prices = {"apple": 0.5, "banana": 0.3}
total = total_value(inv, prices)
print(f"Total value: {total}")
expected_total = (10 * 0.5) + (5 * 0.3) + (3 * 0)  # orange has no price, counts as 0
assert abs(total - expected_total) < 0.0001, f"Expected {expected_total}, got {total}"

print("\nAll tests passed!")
