"""Test script for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item
inv = {}
result = add_item(inv, "apple", 10)
assert result == {"apple": 10}, f"Expected {{'apple': 10}}, got {result}"

# Test add_item accumulates
result = add_item(inv, "apple", 5)
assert result == {"apple": 15}, f"Expected {{'apple': 15}}, got {result}"

# Test add_item with negative qty raises ValueError
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item
inv2 = {"apple": 10, "banana": 5}
result = remove_item(inv2, "apple", 3)
assert result == {"apple": 7, "banana": 5}, f"Got {result}"

# Test remove_item deletes key when qty reaches 0
inv3 = {"apple": 5}
result = remove_item(inv3, "apple", 5)
assert result == {}, f"Expected {{}}, got {result}"

# Test remove_item with unknown name raises KeyError
try:
    remove_item(inv3, "orange", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item with more than available raises ValueError
inv4 = {"apple": 3}
try:
    remove_item(inv4, "apple", 5)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value
inv5 = {"apple": 10, "banana": 5}
prices = {"apple": 1.5, "banana": 2.0}
val = total_value(inv5, prices)
assert val == 10 * 1.5 + 5 * 2.0, f"Expected 25.0, got {val}"

# Test total_value with missing price (should count as 0)
inv6 = {"apple": 10, "orange": 3}
prices2 = {"apple": 1.5}
val2 = total_value(inv6, prices2)
assert val2 == 10 * 1.5, f"Expected 15.0, got {val2}"

print("All tests passed!")
