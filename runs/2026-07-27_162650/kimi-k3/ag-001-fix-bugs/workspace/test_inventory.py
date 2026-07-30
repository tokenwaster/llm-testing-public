from inventory import add_item, remove_item, total_value

# add_item accumulates
inv = {}
assert add_item(inv, "apple", 3) is inv
assert add_item(inv, "apple", 2) is inv
assert inv["apple"] == 5, f"expected 5, got {inv['apple']}"
add_item(inv, "pear", 1)
assert inv == {"apple": 5, "pear": 1}

# add_item negative qty raises ValueError
try:
    add_item(inv, "apple", -1)
    raise AssertionError("expected ValueError")
except ValueError:
    pass

# add zero is allowed
add_item(inv, "apple", 0)
assert inv["apple"] == 5

# remove_item basic
remove_item(inv, "apple", 2)
assert inv["apple"] == 3

# removing to exactly 0 deletes the key
remove_item(inv, "pear", 1)
assert "pear" not in inv

# unknown name raises KeyError
try:
    remove_item(inv, "banana", 1)
    raise AssertionError("expected KeyError")
except KeyError:
    pass

# removing more than available raises ValueError
try:
    remove_item(inv, "apple", 10)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
assert inv["apple"] == 3  # unchanged after failed removal

# remove_item returns the inventory
assert remove_item(inv, "apple", 1) is inv
assert inv["apple"] == 2

# total_value
prices = {"apple": 0.5, "pear": 2.0}
inv = {"apple": 4, "pear": 3}
assert total_value(inv, prices) == 4 * 0.5 + 3 * 2.0

# items missing from prices count as 0
inv = {"apple": 4, "mystery": 100}
assert total_value(inv, prices) == 2.0

# empty inventory
assert total_value({}, prices) == 0

print("All tests passed.")
