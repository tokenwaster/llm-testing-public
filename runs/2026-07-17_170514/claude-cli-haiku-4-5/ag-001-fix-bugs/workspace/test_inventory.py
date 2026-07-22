"""Test inventory.py against specification."""

from inventory import add_item, remove_item, total_value

# Test 1: add_item should accumulate
print("Test 1: add_item accumulation")
inv = {}
add_item(inv, "apple", 5)
print(f"  After adding 5 apples: {inv}")
add_item(inv, "apple", 3)
print(f"  After adding 3 more apples: {inv}")
print(f"  Expected: {{'apple': 8}}, Got: {inv}")
assert inv == {"apple": 8}, f"FAIL: Expected {{'apple': 8}}, got {inv}"
print("  PASS\n")

# Test 2: remove_item unknown name should raise KeyError
print("Test 2: remove_item with unknown name")
inv = {"apple": 5}
try:
    remove_item(inv, "banana", 1)
    print("  FAIL: Should have raised KeyError")
except KeyError as e:
    print(f"  PASS: Raised KeyError for {e}\n")

# Test 3: remove_item more than current should raise ValueError
print("Test 3: remove_item more than current")
inv = {"apple": 5}
try:
    remove_item(inv, "apple", 10)
    print("  FAIL: Should have raised ValueError")
except ValueError as e:
    print(f"  PASS: Raised ValueError: {e}\n")

# Test 4: remove_item should delete key when reaching 0
print("Test 4: remove_item deletes key at 0")
inv = {"apple": 5}
remove_item(inv, "apple", 5)
print(f"  After removing 5 apples: {inv}")
print(f"  Expected: {{}}, Got: {inv}")
assert inv == {}, f"FAIL: Expected {{}}, got {inv}"
print("  PASS\n")

# Test 5: total_value with missing prices should count as 0
print("Test 5: total_value with missing prices")
inv = {"apple": 5, "banana": 3}
prices = {"apple": 2.0}  # banana is missing from prices
result = total_value(inv, prices)
print(f"  Inventory: {inv}")
print(f"  Prices: {prices}")
print(f"  Result: {result}")
print(f"  Expected: 10.0 (5 * 2.0 + 3 * 0), Got: {result}")
# This should be 5*2 + 3*0 = 10
assert result == 10.0, f"FAIL: Expected 10.0, got {result}"
print("  PASS\n")

print("All tests passed!")
