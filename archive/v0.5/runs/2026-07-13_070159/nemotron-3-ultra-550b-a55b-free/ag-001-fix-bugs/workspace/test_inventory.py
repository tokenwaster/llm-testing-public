"""Test script for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item
print("Testing add_item...")
inv = {}
add_item(inv, "apple", 5)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"

# Test accumulation
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"

# Test negative qty raises ValueError
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

print("add_item tests passed!")

# Test remove_item
print("Testing remove_item...")
inv = {"apple": 10, "banana": 5}
remove_item(inv, "apple", 3)
assert inv == {"apple": 7, "banana": 5}, f"Expected {{'apple': 7, 'banana': 5}}, got {inv}"

# Test removing to exactly 0 deletes key
remove_item(inv, "apple", 7)
assert inv == {"banana": 5}, f"Expected {{'banana': 5}}, got {inv}"

# Test unknown name raises KeyError
try:
    remove_item(inv, "orange", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test removing more than available raises ValueError
try:
    remove_item(inv, "banana", 10)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

print("remove_item tests passed!")

# Test total_value
print("Testing total_value...")
inv = {"apple": 10, "banana": 5, "orange": 3}
prices = {"apple": 1.5, "banana": 0.5}
# orange missing from prices, should count as 0
result = total_value(inv, prices)
expected = 10 * 1.5 + 5 * 0.5 + 3 * 0  # = 15 + 2.5 + 0 = 17.5
assert result == expected, f"Expected {expected}, got {result}"

print("total_value tests passed!")

print("\nAll tests passed!")