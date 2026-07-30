"""Quick test for inventory.py."""
from inventory import add_item, remove_item, total_value

# Test 1: add_item should accumulate
inv = {}
add_item(inv, 'apple', 5)
assert inv == {'apple': 5}, f"Expected {{'apple': 5}}, got {inv}"
add_item(inv, 'apple', 3)
assert inv == {'apple': 8}, f"Expected {{'apple': 8}} after accumulation, got {inv}"
print("Test 1 passed: add_item accumulates")

# Test 2: add_item with negative qty raises ValueError
try:
    add_item(inv, 'apple', -1)
    assert False, "Should have raised ValueError"
except ValueError:
    print("Test 2 passed: add_item raises ValueError for negative qty")

# Test 3: remove_item works correctly
inv = {'apple': 5}
remove_item(inv, 'apple', 3)
assert inv == {'apple': 2}, f"Expected {{'apple': 2}}, got {inv}"
print("Test 3 passed: remove_item subtracts correctly")

# Test 4: remove_item deletes key when qty reaches 0
inv = {'apple': 5}
remove_item(inv, 'apple', 5)
assert inv == {}, f"Expected empty dict, got {inv}"
print("Test 4 passed: remove_item deletes key at 0")

# Test 5: remove_item raises KeyError for unknown item
try:
    remove_item({}, 'banana', 1)
    assert False, "Should have raised KeyError"
except KeyError:
    print("Test 5 passed: remove_item raises KeyError for unknown item")

# Test 6: total_value with missing prices should count as 0
inv = {'apple': 2, 'orange': 3}
prices = {'apple': 1.5}
val = total_value(inv, prices)
assert val == 3.0, f"Expected 3.0 (orange counts as 0), got {val}"
print("Test 6 passed: total_value handles missing prices as 0")

# Test 7: total_value normal case
inv = {'apple': 2, 'orange': 3}
prices = {'apple': 1.5, 'orange': 2.0}
val = total_value(inv, prices)
assert val == 9.0, f"Expected 9.0, got {val}"
print("Test 7 passed: total_value normal case")

print("\nAll tests passed!")
