from inventory import add_item, remove_item, total_value

inv = {}

# Test add_item accumulates
add_item(inv, "apple", 5)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"

# Test add_item rejects negative qty
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item removes quantity (partial removal)
remove_item(inv, "apple", 3)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"

# Test remove_item deletes key at zero
remove_item(inv, "apple", 5)
assert "apple" not in inv, f"Key should be deleted, got {inv}"

# Test remove_item raises KeyError for unknown name
try:
    remove_item(inv, "nonexistent", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item raises ValueError when removing more than available (item still exists)
add_item(inv, "apple", 5)
try:
    remove_item(inv, "apple", 6)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value with prices
prices = {"apple": 1.50, "banana": 2.00}
inv = {"apple": 4, "banana": 3}
assert total_value(inv, prices) == 4*1.50 + 3*2.00, f"Got {total_value(inv, prices)}"

# Test total_value: items missing from prices count as 0
inv = {"apple": 4, "mystery": 10}
assert total_value(inv, prices) == 4*1.50 + 0, f"Got {total_value(inv, prices)}"

print("All tests passed!")
