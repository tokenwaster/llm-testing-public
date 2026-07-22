"""Test script for inventory module."""

from inventory import add_item, remove_item, total_value

# Test add_item - accumulation
print("Testing add_item...")
inv = {}
add_item(inv, "apple", 5)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"

add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"
print("  Accumulation test passed")

# Test add_item with qty < 0
try:
    add_item({}, "apple", -1)
    print("  ERROR: Should have raised ValueError for negative qty")
except ValueError:
    print("  Negative qty test passed")

# Test remove_item - unknown name
print("\nTesting remove_item...")
inv = {"apple": 5}
try:
    remove_item(inv, "banana", 1)
    print("  ERROR: Should have raised KeyError for unknown item")
except KeyError:
    print("  Unknown item test passed")

# Test remove_item - more than available
inv = {"apple": 5}
try:
    remove_item(inv, "apple", 10)
    print("  ERROR: Should have raised ValueError for removing too much")
except ValueError:
    print("  Too much stock test passed")

# Test remove_item - deletion when 0
inv = {"apple": 5}
remove_item(inv, "apple", 5)
assert inv == {}, f"Expected {{}}, got {inv}"
print("  Deletion at zero test passed")

# Test total_value - missing price
print("\nTesting total_value...")
inv = {"apple": 5, "banana": 3}
prices = {"apple": 1.0}
result = total_value(inv, prices)
expected = 5 * 1.0 + 3 * 0  # banana missing from prices counts as 0
assert result == expected, f"Expected {expected}, got {result}"
print("  Missing price test passed")

# Test total_value - normal case
inv = {"apple": 5}
prices = {"apple": 2.0}
result = total_value(inv, prices)
assert result == 10.0, f"Expected 10.0, got {result}"
print("  Normal calculation test passed")

print("\nAll tests passed!")
