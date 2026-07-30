from inventory import add_item, remove_item, total_value

# Test add_item - should accumulate
inventory = {}
add_item(inventory, "apple", 5)
assert inventory == {"apple": 5}, f"Expected {{'apple': 5}}, got {inventory}"
add_item(inventory, "apple", 3)
assert inventory == {"apple": 8}, f"Expected {{'apple': 8}}, got {inventory}"

# Test add_item with negative qty
try:
    add_item({}, "apple", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item - unknown name should raise KeyError
try:
    remove_item({}, "apple", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item - more than available should raise ValueError
inventory = {"apple": 5}
try:
    remove_item(inventory, "apple", 10)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item - deletes key when qty reaches 0
inventory = {"apple": 5}
remove_item(inventory, "apple", 5)
assert inventory == {}, f"Expected {{}}, got {inventory}"

# Test total_value - items missing from prices count as 0
inventory = {"apple": 2, "banana": 3, "cherry": 1}
prices = {"apple": 1.5, "banana": 2.0}
expected = 2*1.5 + 3*2.0 + 1*0  # = 3 + 6 + 0 = 9
result = total_value(inventory, prices)
assert result == expected, f"Expected {expected}, got {result}"

print("All tests passed!")
