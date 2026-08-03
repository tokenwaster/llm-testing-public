import traceback
from inventory import add_item, remove_item, total_value

failures = 0

def check(label, got, expected):
    global failures
    if got != expected:
        print(f"FAIL [{label}]: got {got!r}, expected {expected!r}")
        failures += 1
    else:
        print(f"PASS [{label}]")

def expect_raises(label, exc_type, fn, *args, **kwargs):
    global failures
    try:
        fn(*args, **kwargs)
        print(f"FAIL [{label}]: expected {exc_type.__name__} but no exception raised")
        failures += 1
    except exc_type:
        print(f"PASS [{label}]")
    except Exception as e:
        print(f"FAIL [{label}]: expected {exc_type.__name__} but got {type(e).__name__}: {e}")
        failures += 1

# --- add_item ---

# Bug 1: add_item should ACCUMULATE, not overwrite
inv = {"apple": 5}
add_item(inv, "apple", 3)
check("add_item accumulates existing", inv.get("apple"), 8)

# New item should be set
inv2 = {}
add_item(inv2, "banana", 4)
check("add_item new item", inv2.get("banana"), 4)

# Returns inventory
inv3 = {}
ret = add_item(inv3, "x", 1)
check("add_item returns inventory", ret, inv3)

# Negative qty raises ValueError
expect_raises("add_item negative qty", ValueError, add_item, {}, "a", -1)

# qty == 0 is allowed (non-negative)
inv4 = {}
add_item(inv4, "zero", 0)
check("add_item zero qty", inv4.get("zero"), 0)

# --- remove_item ---

# Unknown name raises KeyError
expect_raises("remove_item unknown key", KeyError, remove_item, {}, "ghost", 1)

# Remove more than stock raises ValueError
expect_raises("remove_item over-remove", ValueError, remove_item, {"a": 2}, "a", 5)

# Normal removal
inv5 = {"a": 10}
remove_item(inv5, "a", 3)
check("remove_item normal", inv5.get("a"), 7)

# Exact removal deletes key
inv6 = {"a": 5}
remove_item(inv6, "a", 5)
check("remove_item exact delete", "a" in inv6, False)

# Returns inventory
inv7 = {"a": 3}
ret7 = remove_item(inv7, "a", 1)
check("remove_item returns inventory", ret7, inv7)

# --- total_value ---

# Bug 3: items missing from prices should count as 0, not raise
inv8 = {"apple": 3, "banana": 2, "cherry": 5}
prices = {"apple": 1.0, "banana": 0.5}  # cherry is missing
result = total_value(inv8, prices)
# apple: 3*1.0=3.0, banana: 2*0.5=1.0, cherry: 5*0=0  => 4.0
check("total_value missing price counts as 0", result, 4.0)

# Normal total_value
inv9 = {"x": 2, "y": 3}
prices9 = {"x": 10.0, "y": 5.0}
check("total_value normal", total_value(inv9, prices9), 35.0)

# Empty inventory
check("total_value empty", total_value({}, {"x": 1.0}), 0)

print()
if failures:
    print(f"{failures} test(s) FAILED.")
else:
    print("All tests passed!")
