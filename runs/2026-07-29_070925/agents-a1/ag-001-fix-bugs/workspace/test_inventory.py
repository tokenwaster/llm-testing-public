#!/usr/bin/env python3
"""Test script for inventory module."""

from inventory import add_item, remove_item, total_value

# Test 1: add_item should accumulate quantity
inv = {}
add_item(inv, "widget", 5)
print(f"After first add: {inv}")
assert inv == {"widget": 5}, f"Expected {{'widget': 5}}, got {inv}"

add_item(inv, "widget", 3)
print(f"After second add: {inv}")
assert inv == {"widget": 8}, f"Expected {{'widget': 8}}, got {inv}"
print("Test 1 PASSED")

# Test 2: add_item with negative qty should raise ValueError
try:
    add_item(inv, "gadget", -1)
    print("Test 2 FAILED: Should have raised ValueError")
except ValueError as e:
    print(f"Test 2 PASSED (raised ValueError)")

# Test 3: remove_item removes correct amount and deletes when zero
inv = {"widget": 10, "gadget": 5}
remove_item(inv, "widget", 4)
print(f"After removal of 4 from widget: {inv}")
assert inv == {"widget": 6, "gadget": 5}, f"Unexpected state: {inv}"

remove_item(inv, "gadget", 5)  # Should delete gadget key
print(f"After removing all gadgets: {inv}")
assert inv == {"widget": 6}, f"Expected {{'widget': 6}}, got {inv}"
print("Test 3 PASSED")

# Test 4: remove_item raises KeyError for unknown name
try:
    remove_item(inv, "unknown", 1)
    print("Test 4 FAILED: Should have raised KeyError")
except KeyError as e:
    print(f"Test 4 PASSED (raised KeyError)")

# Test 5: remove_item raises ValueError if removing more than available
inv = {"widget": 3}
try:
    remove_item(inv, "widget", 5)
    print("Test 5 FAILED: Should have raised ValueError")
except ValueError as e:
    print(f"Test 5 PASSED (raised ValueError)")

# Test 6: total_value should treat missing prices as 0
inv = {"item1": 2, "item2": 3}
prices = {"item1": 10}
val = total_value(inv, prices)
print(f"Total value with missing price for item2: {val}")
assert val == 20.0, f"Expected 20.0 (only item1 has price), got {val}"
print("Test 6 PASSED")

# Test 7: total_value returns float even if all prices are present
inv = {"item1": 5}
prices = {"item1": 2.5}
val = total_value(inv, prices)
assert val == 12.5, f"Expected 12.5, got {val}"
print("Test 7 PASSED")

print("\n=== All tests completed ===")
