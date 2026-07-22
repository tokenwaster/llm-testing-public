"""Quick tests for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item accumulation
inv = {}
add_item(inv, "apple", 5)
assert inv["apple"] == 5, f"Expected 5, got {inv['apple']}"
add_item(inv, "apple", 3)
assert inv["apple"] == 8, f"Expected 8 (accumulated), got {inv['apple']}"

# Test add_item negative
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item
inv2 = {"apple": 10}
remove_item(inv2, "apple", 3)
assert inv2["apple"] == 7, f"Expected 7, got {inv2['apple']}"

# Test remove_item unknown key
try:
    remove_item(inv2, "banana", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item too many
try:
    remove_item(inv2, "apple", 100)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item to zero deletes key
inv3 = {"apple": 5}
remove_item(inv3, "apple", 5)
assert "apple" not in inv3, "Key should be deleted when qty reaches 0"

# Test total_value
inv4 = {"apple": 2, "banana": 3}
prices = {"apple": 1.5, "banana": 2.0}
val = total_value(inv4, prices)
assert val == 2*1.5 + 3*2.0, f"Expected 9.0, got {val}"

# Test total_value with missing price (should count as 0)
prices_partial = {"apple": 1.5}
val2 = total_value(inv4, prices_partial)
assert val2 == 2*1.5 + 3*0, f"Expected 3.0, got {val2}"

print("All tests passed!")