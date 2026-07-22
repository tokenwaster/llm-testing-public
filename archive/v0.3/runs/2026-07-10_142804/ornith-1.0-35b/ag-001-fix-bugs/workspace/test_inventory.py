from inventory import add_item, remove_item, total_value

# Test add_item: accumulation
inv = {}
add_item(inv, "apple", 5)
assert inv == {"apple": 5}, f"got {inv}"
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"got {inv}"

# Test add_item: negative qty raises ValueError
try:
    add_item(inv, "apple", -1)
    assert False, "should have raised"
except ValueError:
    pass

# Test remove_item: normal removal
remove_item(inv, "apple", 2)
assert inv == {"apple": 6}, f"got {inv}"

# Test remove_item: reaches 0 -> key deleted
remove_item(inv, "apple", 6)
assert inv == {}, f"got {inv}"

# Test remove_item: unknown name raises KeyError
try:
    remove_item(inv, "banana", 1)
    assert False
except KeyError:
    pass

# Test remove_item: more than available raises ValueError
add_item(inv, "apple", 2)
try:
    remove_item(inv, "apple", 5)
    assert False
except ValueError:
    pass

# Test total_value with missing prices
inv = {"apple": 3, "banana": 10}
prices = {"apple": 1.5}
assert total_value(inv, prices) == 4.5, f"got {total_value(inv, prices)}"

print("All tests passed!")
