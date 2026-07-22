from inventory import add_item, remove_item, total_value

inv = {}

# Test add_item: accumulates with existing quantity
add_item(inv, "apple", 5)
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"

# Test add_item: qty < 0 raises ValueError
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item: removes quantity
remove_item(inv, "apple", 3)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"

# Test remove_item: unknown name raises KeyError
try:
    remove_item(inv, "banana", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item: removing more than available raises ValueError
try:
    remove_item(inv, "apple", 10)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item: quantity reaches exactly 0, key is deleted
remove_item(inv, "apple", 5)
assert inv == {}, f"Expected empty dict, got {inv}"

# Test total_value: items missing from prices count as 0
prices = {"apple": 1.5}
val = total_value({"apple": 8, "banana": 3}, prices)
assert val == 12.0, f"Expected 12.0, got {val}"

# Test total_value: all items have prices
val = total_value({"apple": 4, "banana": 6}, {"apple": 1.5, "banana": 2.0})
assert val == 18.0, f"Expected 18.0, got {val}"

print("All tests passed!")
