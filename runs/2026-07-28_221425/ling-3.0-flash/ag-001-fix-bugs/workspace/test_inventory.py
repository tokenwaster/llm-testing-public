from inventory import add_item, remove_item, total_value

# Test add_item accumulates
inv = {}
add_item(inv, "apple", 5)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"

# Test add_item raises ValueError for negative qty
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item
inv2 = {"apple": 5}
remove_item(inv2, "apple", 3)
assert inv2 == {"apple": 2}, f"Expected {{'apple': 2}}, got {inv2}"

# Test remove_item deletes key when qty reaches 0
remove_item(inv2, "apple", 2)
assert inv2 == {}, f"Expected {{}}, got {inv2}"

# Test remove_item raises KeyError for unknown name
try:
    remove_item(inv2, "banana", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item raises ValueError for too many
inv3 = {"apple": 2}
try:
    remove_item(inv3, "apple", 5)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value with missing price
inv4 = {"apple": 3, "banana": 2}
prices = {"apple": 1.0}
assert total_value(inv4, prices) == 3.0, f"Expected 3.0, got {total_value(inv4, prices)}"

# Test total_value with all prices
prices2 = {"apple": 1.0, "banana": 2.0}
assert total_value(inv4, prices2) == 7.0, f"Expected 7.0, got {total_value(inv4, prices2)}"

print("All tests passed!")
