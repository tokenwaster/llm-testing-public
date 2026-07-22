"""Test script for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item accumulation
inv = {}
add_item(inv, "apple", 5)
print(f"After add apple=5: {inv}")  # {'apple': 5}

add_item(inv, "apple", 3)
print(f"After add apple=3: {inv}")  # Should be {'apple': 8}, not {'apple': 3}
assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"

# Test add_item with negative qty
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    print("add_item correctly raised ValueError for negative qty")

# Test remove_item
inv2 = {"apple": 10, "banana": 5}
remove_item(inv2, "apple", 3)
print(f"After remove apple=3: {inv2}")  # {'apple': 7, 'banana': 5}
assert inv2["apple"] == 7

# Test remove_item to 0 (key should be deleted)
remove_item(inv2, "banana", 5)
print(f"After remove banana=5: {inv2}")  # {'apple': 7}
assert "banana" not in inv2

# Test remove_item unknown name
try:
    remove_item(inv2, "cherry", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    print("remove_item correctly raised KeyError for unknown name")

# Test remove_item more than available
try:
    remove_item(inv2, "apple", 100)
    assert False, "Should have raised ValueError"
except ValueError:
    print("remove_item correctly raised ValueError for over-removal")

# Test total_value with missing prices
inv3 = {"apple": 2, "banana": 3}
prices = {"apple": 1.5}
val = total_value(inv3, prices)
print(f"Total value: {val}")  # Should be 2*1.5 + 3*0 = 3.0
assert val == 3.0, f"Expected 3.0, got {val}"

print("\nAll tests passed!")
