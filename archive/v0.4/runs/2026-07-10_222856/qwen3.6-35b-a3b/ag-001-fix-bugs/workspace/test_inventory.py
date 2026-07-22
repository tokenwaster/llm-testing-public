"""Quick tests for inventory.py fixes."""
from inventory import add_item, remove_item, total_value

# Test add_item accumulation
inv = {}
add_item(inv, "apple", 5)
assert inv["apple"] == 5, f"Expected 5, got {inv['apple']}"
add_item(inv, "apple", 3)
assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"
print("PASS: add_item accumulation")

# Test add_item negative qty raises ValueError
try:
    add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    print("PASS: add_item negative qty raises ValueError")

# Test remove_item
inv2 = {"apple": 10, "banana": 5}
remove_item(inv2, "apple", 3)
assert inv2["apple"] == 7
print("PASS: remove_item")

# Test remove_item deletes key at 0
inv3 = {"apple": 5}
remove_item(inv3, "apple", 5)
assert "apple" not in inv3
print("PASS: remove_item deletes key at 0")

# Test remove_item KeyError
try:
    remove_item(inv3, "apple", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    print("PASS: remove_item KeyError for unknown name")

# Test remove_item ValueError for over-removal
inv4 = {"apple": 3}
try:
    remove_item(inv4, "apple", 5)
    assert False, "Should have raised ValueError"
except ValueError:
    print("PASS: remove_item ValueError for over-removal")

# Test total_value with missing prices
inv5 = {"apple": 2, "banana": 3}
prices = {"apple": 10}
val = total_value(inv5, prices)
assert val == 20 + 0, f"Expected 20, got {val}"
print("PASS: total_value handles missing prices")

# Test total_value normal case
prices2 = {"apple": 10, "banana": 5}
val2 = total_value(inv5, prices2)
assert val2 == 2 * 10 + 3 * 5 == 35, f"Expected 35, got {val2}"
print("PASS: total_value normal case")

print("\nAll tests passed!")
