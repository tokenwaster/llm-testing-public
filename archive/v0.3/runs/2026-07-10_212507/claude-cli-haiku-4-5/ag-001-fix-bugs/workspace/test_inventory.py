"""Test script for inventory.py"""
from inventory import add_item, remove_item, total_value

# Test add_item accumulation
print("Test 1: add_item should accumulate")
inv = {}
add_item(inv, "apple", 5)
print(f"After adding 5 apples: {inv}")
add_item(inv, "apple", 3)
print(f"After adding 3 more apples: {inv}")
print(f"Expected: {{'apple': 8}}, Got: {inv}")
print()

# Test remove_item
print("Test 2: remove_item basic")
inv = {"banana": 10}
remove_item(inv, "banana", 3)
print(f"After removing 3 from 10: {inv}")
print(f"Expected: {{'banana': 7}}")
print()

# Test remove_item deletion at 0
print("Test 3: remove_item should delete at 0")
inv = {"orange": 2}
remove_item(inv, "orange", 2)
print(f"After removing all: {inv}")
print(f"Expected: {{}}")
print()

# Test total_value with missing prices
print("Test 4: total_value with missing prices")
inv = {"apple": 5, "banana": 3}
prices = {"apple": 2.0}
try:
    result = total_value(inv, prices)
    print(f"Total value: {result}")
except KeyError as e:
    print(f"KeyError raised: {e} - this is a BUG!")
    print(f"Expected: should return 5*2.0 + 3*0 = 10.0")
