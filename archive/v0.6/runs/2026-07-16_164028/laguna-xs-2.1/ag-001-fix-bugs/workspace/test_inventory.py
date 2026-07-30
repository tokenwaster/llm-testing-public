"""Test script to verify bugs in inventory.py"""
import inventory

# Test 1: add_item should accumulate
print("Test 1: add_item accumulation")
inv = {}
inventory.add_item(inv, "apples", 5)
print(f"After adding 5 apples: {inv}")
inventory.add_item(inv, "apples", 3)
print(f"After adding 3 more apples: {inv}")
print(f"Expected: {{'apples': 8}}, Got: {inv}")
print(f"PASS" if inv.get("apples") == 8 else "FAIL - add_item doesn't accumulate\n")

# Test 2: remove_item with unknown name
print("\nTest 2: remove_item with unknown name")
inv = {}
try:
    inventory.remove_item(inv, "oranges", 1)
    print("FAIL - should have raised KeyError")
except KeyError as e:
    print(f"PASS - raised KeyError: {e}")

# Test 3: remove_item more than available
print("\nTest 3: remove_item more than available")
inv = {"apples": 3}
try:
    inventory.remove_item(inv, "apples", 5)
    print("FAIL - should have raised ValueError")
except ValueError as e:
    print(f"PASS - raised ValueError: {e}")

# Test 4: remove_item to zero deletes key
print("\nTest 4: remove_item to zero deletes key")
inv = {"apples": 5}
result = inventory.remove_item(inv, "apples", 5)
print(f"After removing 5 from 5: {inv}")
print(f"PASS - key deleted" if "apples" not in inv else "FAIL - key not deleted")

# Test 5: total_value with missing price
print("\nTest 5: total_value with missing price")
inv = {"apples": 5, "oranges": 3}
prices = {"apples": 2.0}  # oranges missing
try:
    total = inventory.total_value(inv, prices)
    print(f"Total: {total}")
    print(f"Expected: 10.0 (5*2 + 3*0), Got: {total}")
    print(f"PASS" if total == 10.0 else "FAIL")
except KeyError as e:
    print(f"FAIL - raised KeyError for missing price: {e}")

# Test 6: add_item with negative qty
print("\nTest 6: add_item with negative qty")
inv = {}
try:
    inventory.add_item(inv, "apples", -1)
    print("FAIL - should have raised ValueError")
except ValueError as e:
    print(f"PASS - raised ValueError: {e}")