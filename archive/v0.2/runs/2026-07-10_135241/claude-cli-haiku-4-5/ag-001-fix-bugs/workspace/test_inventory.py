"""Test script for inventory.py"""
from inventory import add_item, remove_item, total_value

print("Test 1: add_item should accumulate, not replace")
inv = {}
inv = add_item(inv, "apples", 5)
print(f"After first add: {inv}")  # Expected: {'apples': 5}
inv = add_item(inv, "apples", 3)
print(f"After second add: {inv}")  # Expected: {'apples': 8} but got {'apples': 3}

print("\nTest 2: remove_item basic functionality")
inv = {"oranges": 10}
inv = remove_item(inv, "oranges", 3)
print(f"After remove: {inv}")  # Expected: {'oranges': 7}

print("\nTest 3: remove_item deletes key at 0")
inv = {"oranges": 2}
inv = remove_item(inv, "oranges", 2)
print(f"After removing all: {inv}")  # Expected: {}

print("\nTest 4: total_value with all items in prices")
inv = {"apples": 2, "oranges": 3}
prices = {"apples": 1.5, "oranges": 2.0}
value = total_value(inv, prices)
print(f"Total value: {value}")  # Expected: 2*1.5 + 3*2.0 = 9.0

print("\nTest 5: total_value with missing item in prices")
inv = {"apples": 2, "oranges": 3, "bananas": 5}
prices = {"apples": 1.5, "oranges": 2.0}
try:
    value = total_value(inv, prices)
    print(f"Total value: {value}")  # Expected: 2*1.5 + 3*2.0 + 5*0 = 9.0
except KeyError as e:
    print(f"KeyError raised (BUG): {e}")  # Currently raises KeyError
