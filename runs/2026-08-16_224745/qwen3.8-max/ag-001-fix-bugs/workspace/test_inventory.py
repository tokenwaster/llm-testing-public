import inventory as inv


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print("PASS:", msg)


# --- add_item ---
d = {}
r = inv.add_item(d, "apple", 5)
check(r is d and d == {"apple": 5}, "add_item adds new item and returns inventory")
inv.add_item(d, "apple", 3)
check(d == {"apple": 8}, "add_item accumulates with existing quantity")

try:
    inv.add_item(d, "apple", -1)
    check(False, "add_item negative qty raises ValueError")
except ValueError:
    check(True, "add_item negative qty raises ValueError")

# zero qty should be allowed and accumulate
inv.add_item(d, "pear", 0)
check(d.get("pear") == 0, "add_item with qty=0 works")

# --- remove_item ---
d = {"apple": 5}
r = inv.remove_item(d, "apple", 2)
check(r is d and d == {"apple": 3}, "remove_item subtracts and returns inventory")

try:
    inv.remove_item(d, "banana", 1)
    check(False, "remove_item unknown name raises KeyError")
except KeyError:
    check(True, "remove_item unknown name raises KeyError")

try:
    inv.remove_item(d, "apple", 10)
    check(False, "remove_item too much raises ValueError")
except ValueError:
    check(True, "remove_item too much raises ValueError")

inv.remove_item(d, "apple", 3)
check("apple" not in d, "remove_item deletes key when qty reaches 0")

# --- total_value ---
d = {"apple": 2, "banana": 3, "cherry": 10}
prices = {"apple": 1.5, "banana": 2.0}
tv = inv.total_value(d, prices)
check(tv == 2 * 1.5 + 3 * 2.0, f"total_value ignores missing prices (got {tv})")
check(inv.total_value({}, prices) == 0, "total_value of empty inventory is 0")
check(isinstance(inv.total_value(d, prices), float), "total_value returns float")

print("All tests passed.")
