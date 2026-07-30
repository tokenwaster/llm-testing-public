from inventory import add_item, remove_item, total_value

# Test add_item accumulation
inv = {}
add_item(inv, "apple", 5)
add_item(inv, "apple", 3)
assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"
print("add_item accumulation: PASS")

# Test add_item negative raises ValueError
inv2 = {}
try:
    add_item(inv2, "apple", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    print("add_item negative qty raises ValueError: PASS")

# Test remove_item unknown name raises KeyError
inv3 = {"apple": 5}
try:
    remove_item(inv3, "banana", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    print("remove_item unknown name raises KeyError: PASS")

# Test remove_item over-removal raises ValueError
inv4 = {"apple": 5}
try:
    remove_item(inv4, "apple", 10)
    assert False, "Should have raised ValueError"
except ValueError:
    print("remove_item over-removal raises ValueError: PASS")

# Test remove_item deletes key at 0
inv5 = {"apple": 5}
remove_item(inv5, "apple", 5)
assert "apple" not in inv5, "Key should be deleted"
print("remove_item deletes key at 0: PASS")

# Test remove_item returns inventory
inv6 = {"apple": 5}
result = remove_item(inv6, "apple", 2)
assert result is inv6, "Should return the inventory dict"
print("remove_item returns inventory: PASS")

# Test total_value missing price counts as 0
inv7 = {"apple": 5, "banana": 3}
prices = {"apple": 2.0}  # banana missing
val = total_value(inv7, prices)
assert val == 10.0, f"Expected 10.0, got {val}"
print("total_value missing price counts as 0: PASS")

# Test total_value normal
inv8 = {"apple": 5, "banana": 3}
prices8 = {"apple": 2.0, "banana": 1.0}
val8 = total_value(inv8, prices8)
assert val8 == 13.0, f"Expected 13.0, got {val8}"
print("total_value normal: PASS")

print("\nAll tests passed!")
