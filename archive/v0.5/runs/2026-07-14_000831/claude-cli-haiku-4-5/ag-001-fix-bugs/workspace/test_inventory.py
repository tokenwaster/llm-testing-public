"""Test script for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test 1: add_item should accumulate, not replace
inv = {}
add_item(inv, "apple", 5)
print(f"After adding 5 apples: {inv}")
add_item(inv, "apple", 3)
print(f"After adding 3 more apples: {inv}")
print(f"Expected: {{'apple': 8}}, Got: {inv}")
assert inv["apple"] == 8, f"add_item should accumulate! Got {inv['apple']}"

# Test 2: remove_item should work correctly (seems OK based on code)
inv = {"orange": 10}
remove_item(inv, "orange", 3)
print(f"\nAfter removing 3 oranges from 10: {inv}")
assert inv["orange"] == 7

# Test 3: remove_item should delete key when qty reaches 0
inv = {"banana": 2}
remove_item(inv, "banana", 2)
print(f"After removing all bananas: {inv}")
assert "banana" not in inv

# Test 4: total_value with missing prices should count as 0, not raise
inv = {"apple": 5, "unknown": 10}
prices = {"apple": 2.0}
print(f"\nInventory: {inv}, Prices: {prices}")
try:
    total = total_value(inv, prices)
    print(f"Total value: {total}")
    print(f"Expected: 10.0 (5*2 + 10*0), Got: {total}")
except KeyError as e:
    print(f"ERROR: KeyError raised for missing price: {e}")
    print("total_value should treat missing prices as 0!")

print("\nAll tests would pass if bugs are fixed!")
