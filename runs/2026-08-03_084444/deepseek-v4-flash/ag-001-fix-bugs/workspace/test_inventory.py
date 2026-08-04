from inventory import add_item, remove_item, total_value

# --- Test add_item accumulation ---
inv = {}
add_item(inv, "apple", 5)
add_item(inv, "apple", 3)
assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"
print("add_item accumulation: OK")

# --- Test add_item negative qty ---
try:
    add_item(inv, "bad", -1)
    assert False, "Should have raised ValueError"
except ValueError:
    print("add_item ValueError: OK")

# --- Test remove_item ---
remove_item(inv, "apple", 2)
assert inv["apple"] == 6
print("remove_item basic: OK")

# --- Test remove_item removes key at zero ---
remove_item(inv, "apple", 6)
assert "apple" not in inv
print("remove_item removes key at zero: OK")

# --- Test remove_item unknown name ---
try:
    remove_item(inv, "ghost", 1)
    assert False, "Should have raised KeyError"
except KeyError:
    print("remove_item KeyError: OK")

# --- Test remove_item over-removal ---
inv["banana"] = 3
try:
    remove_item(inv, "banana", 4)
    assert False, "Should have raised ValueError"
except ValueError:
    print("remove_item ValueError: OK")

# --- Test total_value ---
inv2 = {"a": 10, "b": 5, "c": 2}
prices = {"a": 1.5, "b": 2.0}  # c missing -> counts as 0
val = total_value(inv2, prices)
expected = 10*1.5 + 5*2.0 + 2*0
assert val == expected, f"Expected {expected}, got {val}"
print("total_value missing-prices (count as 0): OK")

print("\nAll tests passed!")