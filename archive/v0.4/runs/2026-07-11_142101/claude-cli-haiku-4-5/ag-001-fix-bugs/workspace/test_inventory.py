"""Test inventory.py against the spec."""
from inventory import add_item, remove_item, total_value

# Test 1: add_item should accumulate
inv = {}
add_item(inv, "apple", 5)
add_item(inv, "apple", 3)
print(f"Test 1 (add accumulates): {inv}")  # Should be {'apple': 8}, not {'apple': 3}

# Test 2: remove_item with unknown name
inv = {}
try:
    remove_item(inv, "banana", 1)
except KeyError:
    print("Test 2 (remove unknown raises KeyError): PASS")

# Test 3: remove_item exceeding stock
inv = {"apple": 5}
try:
    remove_item(inv, "apple", 10)
except ValueError:
    print("Test 3 (remove too much raises ValueError): PASS")

# Test 4: remove_item deleting at 0
inv = {"apple": 5}
remove_item(inv, "apple", 5)
print(f"Test 4 (remove to 0 deletes key): {inv}")  # Should be {}

# Test 5: total_value with missing prices
inv = {"apple": 5, "banana": 3}
prices = {"apple": 2.0}  # banana not in prices
try:
    result = total_value(inv, prices)
    expected = 5 * 2.0 + 3 * 0  # banana missing should count as 0
    if result == expected:
        print(f"Test 5 (missing prices count as 0): PASS - got {result}")
    else:
        print(f"Test 5 (missing prices): FAIL - got {result}, expected {expected}")
except KeyError:
    print("Test 5 (missing prices raises KeyError): FAIL - should count as 0")

# Test 6: total_value with all prices
inv = {"apple": 5, "banana": 3}
prices = {"apple": 2.0, "banana": 1.5}
result = total_value(inv, prices)
print(f"Test 6 (total_value): {result}")  # Should be 5*2.0 + 3*1.5 = 14.5
