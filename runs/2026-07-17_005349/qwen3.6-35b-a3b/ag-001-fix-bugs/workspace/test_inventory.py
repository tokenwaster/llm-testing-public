from inventory import add_item, remove_item, total_value

# Test add_item - accumulation
inv = {}
add_item(inv, "apple", 10)
assert inv["apple"] == 10, f"Expected 10, got {inv['apple']}"
add_item(inv, "apple", 5)
assert inv["apple"] == 15, f"Expected 15, got {inv['apple']}"

# Test add_item - negative qty raises ValueError
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item - normal removal
inv2 = {"apple": 10}
remove_item(inv2, "apple", 3)
assert inv2["apple"] == 7

# Test remove_item - removes key when qty reaches 0
inv3 = {"apple": 5}
remove_item(inv3, "apple", 5)
assert "apple" not in inv3

# Test remove_item - unknown name raises KeyError
try:
    remove_item(inv3, "banana", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item - removing more than available raises ValueError
inv4 = {"apple": 3}
try:
    remove_item(inv4, "apple", 5)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test total_value - items missing from prices count as 0
inv5 = {"apple": 10, "banana": 5}
prices = {"apple": 2.0}
val = total_value(inv5, prices)
assert val == 20.0, f"Expected 20.0, got {val}"

# Test total_value - normal case
prices2 = {"apple": 2.0, "banana": 3.0}
val2 = total_value(inv5, prices2)
assert val2 == 35.0, f"Expected 35.0, got {val2}"

print("All tests passed!")
