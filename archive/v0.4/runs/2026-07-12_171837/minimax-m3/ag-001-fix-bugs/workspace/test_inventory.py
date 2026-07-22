"""Test script to validate inventory.py against its spec."""
import inventory as inv


def expect(label, cond):
    status = "PASS" if cond else "FAIL"
    print(f"{status}: {label}")


# add_item: basic addition
inv1 = {}
inv.add_item(inv1, "apple", 5)
expect("add 5 apples", inv1 == {"apple": 5})

# add_item: accumulation
inv.add_item(inv1, "apple", 3)
expect("accumulate to 8", inv1 == {"apple": 8})

# add_item: negative qty raises ValueError
try:
    inv.add_item(inv1, "apple", -1)
    expect("negative qty raises", False)
except ValueError:
    expect("negative qty raises", True)

# remove_item: known item
inv2 = {"apple": 5}
inv.remove_item(inv2, "apple", 2)
expect("remove partial", inv2 == {"apple": 3})

# remove_item: exactly 0 deletes key
inv.remove_item(inv2, "apple", 3)
expect("removal to 0 deletes key", inv2 == {})

# remove_item: unknown raises KeyError
try:
    inv.remove_item({"apple": 1}, "banana", 1)
    expect("unknown raises KeyError", False)
except KeyError:
    expect("unknown raises KeyError", True)

# remove_item: too many raises ValueError
try:
    inv.remove_item({"apple": 1}, "apple", 5)
    expect("over-remove raises", False)
except ValueError:
    expect("over-remove raises", True)

# total_value: basic
total = inv.total_value({"apple": 2, "banana": 3}, {"apple": 1.0, "banana": 0.5})
expect("total 2*1.0 + 3*0.5 = 3.5", total == 3.5)

# total_value: missing price -> 0
total2 = inv.total_value({"apple": 2, "banana": 3}, {"apple": 1.0})
expect("missing price counts as 0", total2 == 2.0)

# total_value: empty inventory
total3 = inv.total_value({}, {"apple": 1.0})
expect("empty inventory totals 0", total3 == 0)
