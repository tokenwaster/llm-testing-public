"""Quick tests for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item accumulates
inv = {}
add_item(inv, "apple", 5)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"

# Test add_item raises on negative qty
try:
    add_item(inv, "apple", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item
inv2 = {"banana": 10}
remove_item(inv2, "banana", 10)
assert inv2 == {}, f"Expected empty dict, got {inv2}"

# Test remove_item raises on unknown name
try:
    remove_item({}, "mango", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item raises on over-removal
try:
    remove_item({"apple": 2}, "apple", 5)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value with missing prices counts as 0
inv3 = {"apple": 3, "banana": 2}
prices = {"apple": 1.5}
val = total_value(inv3, prices)
assert val == 4.5, f"Expected 4.5, got {val}"

print("All tests passed!")
