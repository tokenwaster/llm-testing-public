"""Quick test script for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item
inv = {}
result = add_item(inv, "apple", 10)
assert inv == {"apple": 10}, f"Expected {{'apple': 10}}, got {inv}"

# Accumulation
result = add_item(inv, "apple", 5)
assert inv == {"apple": 15}, f"Expected {{'apple': 15}}, got {inv}"

# Negative qty should raise ValueError
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item
inv2 = {"apple": 10, "banana": 5}
result = remove_item(inv2, "apple", 3)
assert inv2 == {"apple": 7, "banana": 5}, f"Got {inv2}"

# Remove all of an item (should delete key)
result = remove_item(inv2, "banana", 5)
assert inv2 == {"apple": 7}, f"Got {inv2}"

# Remove from unknown name should raise KeyError
try:
    remove_item(inv2, "cherry", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Remove more than available should raise ValueError
try:
    remove_item(inv2, "apple", 100)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value
inv3 = {"apple": 10, "banana": 5}
prices = {"apple": 1.5, "banana": 0.75}
val = total_value(inv3, prices)
expected = 10 * 1.5 + 5 * 0.75  # 15 + 3.75 = 18.75
assert val == expected, f"Expected {expected}, got {val}"

# Items missing from prices should count as 0
prices2 = {"apple": 1.5}  # banana missing
val2 = total_value(inv3, prices2)
expected2 = 10 * 1.5 + 5 * 0  # 15 + 0 = 15
assert val2 == expected2, f"Expected {expected2}, got {val2}"

print("All tests passed!")
