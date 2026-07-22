"""Test script for inventory.py"""
from inventory import add_item, remove_item, total_value

print("Testing add_item...")
inv = {}

# Test: accumulation (not replacement)
add_item(inv, "apple", 5)
print(f"After adding 5 apples: {inv}")
add_item(inv, "apple", 3)
print(f"After adding 3 more apples: {inv}")
assert inv["apple"] == 8, f"Expected 8 apples, got {inv['apple']}"
print("PASS: accumulation works\n")

# Test: negative qty raises ValueError
try:
    add_item(inv, "banana", -1)
    print("FAIL: add_item should raise ValueError for negative qty")
except ValueError:
    print("PASS: add_item raises ValueError for negative qty\n")

print("Testing remove_item...")
inv = {"apple": 10, "banana": 5}

# Test: remove existing item
remove_item(inv, "apple", 3)
print(f"After removing 3 apples: {inv}")
assert inv["apple"] == 7, f"Expected 7 apples, got {inv['apple']}"
print("PASS: remove works\n")

# Test: remove to zero deletes key
remove_item(inv, "banana", 5)
print(f"After removing all bananas: {inv}")
assert "banana" not in inv, "Key should be deleted when qty reaches 0"
print("PASS: key deleted when qty reaches 0\n")

# Test: unknown item raises KeyError
try:
    remove_item(inv, "orange", 1)
    print("FAIL: remove_item should raise KeyError for unknown item")
except KeyError:
    print("PASS: remove_item raises KeyError for unknown item\n")

# Test: removing too much raises ValueError
try:
    remove_item(inv, "apple", 100)
    print("FAIL: remove_item should raise ValueError for removing too much")
except ValueError:
    print("PASS: remove_item raises ValueError for removing too much\n")

print("Testing total_value...")
inv = {"apple": 5, "banana": 2, "orange": 3}
prices = {"apple": 1.0, "banana": 2.0}  # orange is missing

# Test: items missing from prices count as 0
total = total_value(inv, prices)
print(f"Inventory: {inv}")
print(f"Prices: {prices}")
print(f"Total value: {total}")
expected = 5 * 1.0 + 2 * 2.0 + 3 * 0  # orange counts as 0
assert total == expected, f"Expected {expected}, got {total}"
print("PASS: items missing from prices count as 0\n")

print("All tests passed!")
