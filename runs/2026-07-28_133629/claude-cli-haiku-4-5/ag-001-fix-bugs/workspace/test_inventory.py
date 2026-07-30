import inventory

# Test 1: add_item should accumulate, not replace
inv = {}
inventory.add_item(inv, "apple", 5)
inventory.add_item(inv, "apple", 3)
print(f"Test 1 - add_item accumulation: {inv}")
assert inv["apple"] == 8, f"Expected 8 apples, got {inv['apple']}"
print("PASS: Test 1 passed")

# Test 2: remove_item basic functionality
inv = {"apple": 10}
inventory.remove_item(inv, "apple", 3)
print(f"Test 2 - remove_item: {inv}")
assert inv["apple"] == 7, f"Expected 7 apples, got {inv['apple']}"
print("PASS: Test 2 passed")

# Test 3: remove_item deletes at 0
inv = {"apple": 5}
inventory.remove_item(inv, "apple", 5)
print(f"Test 3 - remove_item to 0: {inv}")
assert "apple" not in inv, f"Expected key deleted, but {inv}"
print("PASS: Test 3 passed")

# Test 4: total_value with missing prices (should count as 0, not raise)
inv = {"apple": 5, "banana": 3}
prices = {"apple": 2.0}  # banana price is missing
try:
    total = inventory.total_value(inv, prices)
    print(f"Test 4 - total_value with missing price: {total}")
    assert total == 10.0, f"Expected 10.0 (5*2 + 3*0), got {total}"
    print("PASS: Test 4 passed")
except KeyError as e:
    print(f"FAIL: Test 4 failed: KeyError {e} (missing prices should count as 0)")
