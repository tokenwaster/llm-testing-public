from inventory import add_item, remove_item, total_value

# Test add_item accumulation
inv = {}
add_item(inv, "apple", 5)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"

# Test add_item ValueError
try:
    add_item(inv, "apple", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item
inv = {"apple": 8}
remove_item(inv, "apple", 3)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"

# Test remove_item KeyError
try:
    remove_item(inv, "banana", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

# Test remove_item ValueError (removing more than available)
try:
    remove_item(inv, "apple", 100)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

# Test remove_item deletes key at 0
inv = {"apple": 5}
remove_item(inv, "apple", 5)
assert inv == {}, f"Expected {{}}, got {inv}"

# Test total_value with missing prices (should count as 0)
inv = {"apple": 5, "banana": 3}
prices = {"apple": 2.0}
result = total_value(inv, prices)
assert result == 10.0, f"Expected 10.0, got {result}"

print("All tests passed!")
