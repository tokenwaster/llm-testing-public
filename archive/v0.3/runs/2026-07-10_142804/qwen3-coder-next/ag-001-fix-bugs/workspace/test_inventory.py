"""Test script for inventory module."""
from inventory import add_item, remove_item, total_value

# Test add_item - accumulation
print("Testing add_item...")
inv = {"apple": 5}
add_item(inv, "apple", 3)
assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"
print("  Accumulation: PASS")

# Test add_item with new item
inv2 = {}
add_item(inv2, "banana", 10)
assert inv2["banana"] == 10, f"Expected 10, got {inv2['banana']}"
print("  New item: PASS")

# Test add_item raises ValueError for negative qty
try:
    add_item({}, "item", -5)
    print("  Negative qty: FAIL (no exception)")
except ValueError:
    print("  Negative qty: PASS")

# Test remove_item with unknown name
print("\nTesting remove_item...")
try:
    remove_item({}, "unknown", 1)
    print("  Unknown name: FAIL (no exception)")
except KeyError:
    print("  Unknown name: PASS")

# Test remove_item raises ValueError for too much
inv3 = {"apple": 5}
try:
    remove_item(inv3, "apple", 10)
    print("  Too much stock: FAIL (no exception)")
except ValueError:
    print("  Too much stock: PASS")

# Test remove_item deletes key at 0
inv4 = {"apple": 5}
remove_item(inv4, "apple", 5)
assert "apple" not in inv4, f"Expected 'apple' to be deleted"
print("  Delete at zero: PASS")

# Test total_value with missing price
print("\nTesting total_value...")
inv5 = {"apple": 3, "banana": 2}
prices5 = {"apple": 1.5}
result = total_value(inv5, prices5)
assert result == 4.5, f"Expected 4.5, got {result}"
print("  Missing price counts as 0: PASS")

# Test normal total_value
inv6 = {"apple": 3, "banana": 2}
prices6 = {"apple": 1.5, "banana": 2.0}
result = total_value(inv6, prices6)
assert result == 8.5, f"Expected 8.5, got {result}"
print("  Normal calculation: PASS")

print("\nAll tests passed!")
