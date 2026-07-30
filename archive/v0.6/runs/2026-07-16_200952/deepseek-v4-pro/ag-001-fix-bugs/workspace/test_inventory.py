"""Quick tests for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item accumulation
inv = {}
add_item(inv, "apple", 5)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"

# Test add_item negative
try:
    add_item(inv, "apple", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item
inv2 = {"banana": 10}
remove_item(inv2, "banana", 3)
assert inv2 == {"banana": 7}, f"Expected {{'banana': 7}}, got {inv2}"

# Test remove_item unknown key
try:
    remove_item(inv2, "orange", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item too many
try:
    remove_item(inv2, "banana", 100)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item to zero deletes key
inv3 = {"kiwi": 5}
remove_item(inv3, "kiwi", 5)
assert "kiwi" not in inv3, f"Key 'kiwi' should be deleted, got {inv3}"

# Test total_value
inv4 = {"apple": 2, "banana": 3}
prices = {"apple": 1.5, "banana": 2.0}
assert total_value(inv4, prices) == 2*1.5 + 3*2.0, "total_value wrong"

# Test total_value with missing price
prices2 = {"apple": 1.5}
assert total_value(inv4, prices2) == 2*1.5 + 3*0, "total_value should treat missing as 0"

print("All tests passed!")