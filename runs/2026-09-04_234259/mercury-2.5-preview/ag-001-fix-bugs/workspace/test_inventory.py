from inventory import add_item, remove_item, total_value

# Test add_item accumulation
inv = {}
add_item(inv, "apple", 5)
add_item(inv, "apple", 3)
assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"

# Test remove_item
inv = {"apple": 10}
remove_item(inv, "apple", 3)
assert inv["apple"] == 7

# Test total_value with missing prices
inv = {"apple": 5, "banana": 3}
prices = {"apple": 2}
result = total_value(inv, prices)
assert result == 10, f"Expected 10, got {result}"

print("All tests passed!")
