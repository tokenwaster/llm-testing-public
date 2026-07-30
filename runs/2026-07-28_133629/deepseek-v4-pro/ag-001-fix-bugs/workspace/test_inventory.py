import inventory

# Test add_item
inv = {}
inventory.add_item(inv, "apple", 5)
assert inv == {"apple": 5}, f"Expected {{'apple': 5}}, got {inv}"

inventory.add_item(inv, "apple", 3)
assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"  # should accumulate!

inv2 = {}
try:
    inventory.add_item(inv2, "bad", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

print("add_item: OK")

# Test remove_item
inv = {"apple": 10, "banana": 3}
inventory.remove_item(inv, "apple", 5)
assert inv == {"apple": 5, "banana": 3}, f"Got {inv}"

inventory.remove_item(inv, "apple", 5)
assert inv == {"banana": 3}, f"Expected apple deleted, got {inv}"

try:
    inventory.remove_item(inv, "apple", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    pass

try:
    inventory.remove_item(inv, "banana", 10)
    assert False, "Should have raised ValueError"
except ValueError:
    pass

print("remove_item: OK")

# Test total_value
inv = {"apple": 2, "banana": 3, "cherry": 1}
prices = {"apple": 1.5, "banana": 0.5}
# cherry missing from prices -> should count as 0
total = inventory.total_value(inv, prices)
assert total == 2*1.5 + 3*0.5 + 1*0, f"Expected 4.5, got {total}"
print(f"total_value: OK, got {total}")

print("\nAll tests passed!")
