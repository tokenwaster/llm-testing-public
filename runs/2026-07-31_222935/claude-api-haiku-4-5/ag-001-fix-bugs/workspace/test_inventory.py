#!/usr/bin/env python3
import inventory

# Test add_item
print("=== Testing add_item ===")
inv = {}
result = inventory.add_item(inv, "apple", 5)
print(f"After adding 5 apples: {inv}")
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"

# Test accumulation
result = inventory.add_item(inv, "apple", 3)
print(f"After adding 3 more apples: {inv}")
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"

# Test negative qty
try:
    inventory.add_item(inv, "banana", -1)
    assert False, "Should have raised ValueError for negative qty"
except ValueError:
    print("Correctly raised ValueError for negative qty")

print("\n=== Testing remove_item ===")
inv = {"apple": 10, "banana": 5}

# Test normal removal
result = inventory.remove_item(inv, "apple", 3)
print(f"After removing 3 apples: {inv}")
assert inv == {"apple": 7, "banana": 5}, f"Expected {{'apple': 7, 'banana': 5}}, got {inv}"

# Test removal to zero (key should be deleted)
result = inventory.remove_item(inv, "banana", 5)
print(f"After removing 5 bananas (to zero): {inv}")
assert inv == {"apple": 7}, f"Expected {{'apple': 7}}, got {inv}"

# Test unknown name
try:
    inventory.remove_item(inv, "grape", 1)
    assert False, "Should have raised KeyError for unknown name"
except KeyError:
    print("Correctly raised KeyError for unknown name")

# Test removing more than available
try:
    inventory.remove_item(inv, "apple", 10)
    assert False, "Should have raised ValueError for overremoval"
except ValueError:
    print("Correctly raised ValueError for removing more than available")

print("\n=== Testing total_value ===")
inv = {"apple": 5, "banana": 3, "orange": 2}
prices = {"apple": 1.5, "banana": 0.5, "orange": 2.0}

value = inventory.total_value(inv, prices)
expected = 5 * 1.5 + 3 * 0.5 + 2 * 2.0  # 7.5 + 1.5 + 4.0 = 13.0
print(f"Total value with all items in prices: {value}")
assert value == expected, f"Expected {expected}, got {value}"

# Test with missing items in prices (should count as 0)
prices2 = {"apple": 1.5}
value2 = inventory.total_value(inv, prices2)
expected2 = 5 * 1.5  # only apple, others count as 0
print(f"Total value with missing items: {value2}")
assert value2 == expected2, f"Expected {expected2}, got {value2}"

print("\n=== All tests passed! ===")
