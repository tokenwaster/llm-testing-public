import inventory

# Test 1: add_item should accumulate
inv = {}
inventory.add_item(inv, "apples", 5)
print(f"After adding apples=5: {inv}")
inventory.add_item(inv, "apples", 3)
print(f"After adding apples=3 more: {inv}")
# Expected: {"apples": 8}, but bug would make it {"apples": 3}

# Test 2: add_item should raise ValueError for negative qty
try:
    inventory.add_item(inv, "oranges", -1)
    print("ERROR: Should have raised ValueError")
except ValueError as e:
    print(f"Correctly raised ValueError: {e}")

# Test 3: remove_item from unknown item raises KeyError
try:
    inventory.remove_item(inv, "bananas", 2)
    print("ERROR: Should have raised KeyError")
except KeyError as e:
    print(f"Correctly raised KeyError: {e}")

# Test 4: remove more than available raises ValueError
inventory.add_item(inv, "apples", 10)  # total apples = 18
try:
    inventory.remove_item(inv, "apples", 100)
    print("ERROR: Should have raised ValueError")
except ValueError as e:
    print(f"Correctly raised ValueError: {e}")

# Test 5: remove to zero deletes key
inventory.add_item(inv, "to_delete", 5)
print(f"Before removing 5: {inv}")
result = inventory.remove_item(inv, "to_delete", 5)
print(f"After removing 5 (should be deleted): {inv}")

# Test 6: total_value - items missing from prices should count as 0
prices = {"apples": 2.0}
total = inventory.total_value({"apples": 10, "missing_item": 5}, prices)
print(f"Total value (should be 20.0): {total}")

print("\nAll tests complete!")