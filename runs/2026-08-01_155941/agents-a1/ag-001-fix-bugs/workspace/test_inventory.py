#!/usr/bin/env python3
from inventory import add_item, remove_item, total_value

# Test 1: add_item accumulates with existing quantity
inv = {"apple": 5}
add_item(inv, "apple", 3)
assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"
print("Test 1 passed: add_item accumulates")

# Test 2: add_item raises ValueError for negative qty
try:
    add_item({}, "x", -1)
    assert False, "Should have raised ValueError"
except ValueError as e:
    print(f"Test 2 passed: ValueError raised ({e})")

# Test 3: remove_item deletes key at zero
inv = {"apple": 5}
remove_item(inv, "apple", 5)
assert "apple" not in inv, f"Key should be deleted, got {inv}"
print("Test 3 passed: key deleted at zero")

# Test 4: remove_item raises KeyError for unknown name
try:
    remove_item({}, "x", 1)
    assert False, "Should have raised KeyError"
except KeyError as e:
    print(f"Test 4 passed: KeyError raised ({e})")

# Test 5: total_value handles missing prices gracefully
inv = {"apple": 2}
prices = {}
val = total_value(inv, prices)
assert val == 0, f"Expected 0, got {val}"
print("Test 5 passed: missing price returns 0")

# Test 6: total_value returns float type
inv = {"a": 1}
prices = {"a": 2.5}
val = total_value(inv, prices)
assert isinstance(val, float), f"Expected float, got {type(val)}"
print("Test 6 passed: returns float")

print("\nAll tests passed!")
