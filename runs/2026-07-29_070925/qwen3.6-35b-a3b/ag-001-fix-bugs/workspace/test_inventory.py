from inventory import add_item, remove_item, total_value

# Test add_item
inv = {}
add_item(inv, "apple", 10)
assert inv["apple"] == 10

# Accumulating quantities
add_item(inv, "apple", 5)
assert inv["apple"] == 15

# Negative qty raises ValueError
try:
    add_item(inv, "banana", -3)
    assert False, "Should have raised"
except ValueError:
    pass

# Test remove_item
remove_item(inv, "apple", 10)
assert inv["apple"] == 5

# Removing all stock deletes the key
remove_item(inv, "apple", 5)
assert "apple" not in inv

# Unknown name raises KeyError
try:
    remove_item(inv, "mango", 1)
    assert False, "Should have raised"
except KeyError:
    pass

# Removing more than available raises ValueError
add_item(inv, "banana", 3)
try:
    remove_item(inv, "banana", 5)
    assert False, "Should have raised"
except ValueError:
    pass

# Test total_value
inv = {"apple": 10, "banana": 20}
prices = {"apple": 1.5, "orange": 2.0}  # banana missing from prices counts as 0
val = total_value(inv, prices)
assert val == 10 * 1.5 + 20 * 0, f"Expected 15.0, got {val}"

print("All tests passed!")
