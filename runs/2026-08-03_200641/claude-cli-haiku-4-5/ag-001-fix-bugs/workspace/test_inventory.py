#!/usr/bin/env python3
"""Test script to verify inventory.py behavior."""

from inventory import add_item, remove_item, total_value

# Test add_item accumulation
print("Test 1: add_item should accumulate")
inv = {"apple": 5}
result = add_item(inv, "apple", 3)
print(f"  After adding 3 apples to 5: {result}")
print(f"  Expected: {{'apple': 8}}, Got: {result}")
assert result["apple"] == 8, f"Expected 8, got {result['apple']}"
print("  [PASSED]\n")

# Test add_item with new item
print("Test 2: add_item with new item")
inv = {}
result = add_item(inv, "banana", 2)
print(f"  After adding 2 bananas: {result}")
assert result["banana"] == 2, f"Expected 2, got {result['banana']}"
print("  [PASSED]\n")

# Test add_item with negative qty
print("Test 3: add_item with negative qty should raise ValueError")
inv = {}
try:
    add_item(inv, "orange", -1)
    print("  ✗ FAILED: Should have raised ValueError")
except ValueError as e:
    print(f"  Raised ValueError: {e}")
    print("  [PASSED]\n")

# Test remove_item unknown name
print("Test 4: remove_item with unknown name should raise KeyError")
inv = {"apple": 5}
try:
    remove_item(inv, "grape", 1)
    print("  ✗ FAILED: Should have raised KeyError")
except KeyError as e:
    print(f"  Raised KeyError: {e}")
    print("  [PASSED]\n")

# Test remove_item too much
print("Test 5: remove_item with qty > existing should raise ValueError")
inv = {"apple": 5}
try:
    remove_item(inv, "apple", 10)
    print("  ✗ FAILED: Should have raised ValueError")
except ValueError as e:
    print(f"  Raised ValueError: {e}")
    print("  [PASSED]\n")

# Test remove_item to zero
print("Test 6: remove_item to exactly zero should delete key")
inv = {"apple": 5}
result = remove_item(inv, "apple", 5)
print(f"  After removing 5 apples from 5: {result}")
assert "apple" not in result, f"Expected key deleted, but apple still present"
print("  [PASSED]\n")

# Test remove_item partial
print("Test 7: remove_item partial removal")
inv = {"apple": 5}
result = remove_item(inv, "apple", 2)
print(f"  After removing 2 apples from 5: {result}")
assert result["apple"] == 3, f"Expected 3, got {result['apple']}"
print("  [PASSED]\n")

# Test total_value normal case
print("Test 8: total_value with all items in prices")
inv = {"apple": 2, "banana": 3}
prices = {"apple": 1.5, "banana": 0.5}
result = total_value(inv, prices)
print(f"  2 apples @ 1.5 + 3 bananas @ 0.5 = {result}")
expected = 2 * 1.5 + 3 * 0.5
assert result == expected, f"Expected {expected}, got {result}"
print("  [PASSED]\n")

# Test total_value with missing item in prices
print("Test 9: total_value with missing item in prices (should count as 0)")
inv = {"apple": 2, "orange": 3}
prices = {"apple": 1.5}
try:
    result = total_value(inv, prices)
    print(f"  Result: {result}")
    expected = 2 * 1.5 + 3 * 0
    assert result == expected, f"Expected {expected}, got {result}"
    print("  [PASSED]\n")
except KeyError as e:
    print(f"  ✗ FAILED: Raised KeyError {e} but should count missing items as 0\n")

print("All tests completed!")
