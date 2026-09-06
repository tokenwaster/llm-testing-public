import inventory as inv


def check(label, fn, expected=None, exc=None):
    try:
        got = fn()
    except Exception as e:
        if exc and isinstance(e, exc):
            print(f"PASS {label}: raised {type(e).__name__}")
        else:
            print(f"FAIL {label}: unexpected {type(e).__name__}: {e}")
        return
    if exc:
        print(f"FAIL {label}: expected {exc.__name__}, got {got!r}")
    elif got == expected:
        print(f"PASS {label}: {got!r}")
    else:
        print(f"FAIL {label}: got {got!r}, expected {expected!r}")


# add_item accumulates
d = {}
check("add new", lambda: inv.add_item(d, "apple", 5), {"apple": 5})
check("add accumulates", lambda: inv.add_item(d, "apple", 3), {"apple": 8})
check("add other", lambda: inv.add_item(d, "pear", 2), {"apple": 8, "pear": 2})
check("add zero", lambda: inv.add_item(d, "pear", 0), {"apple": 8, "pear": 2})
check("add negative", lambda: inv.add_item(d, "pear", -1), exc=ValueError)
check("add returns same obj", lambda: inv.add_item(d, "pear", 1) is d, True)

# remove_item
d = {"apple": 8, "pear": 3}
check("remove some", lambda: inv.remove_item(d, "apple", 3), {"apple": 5, "pear": 3})
check("remove to zero deletes", lambda: inv.remove_item(d, "pear", 3), {"apple": 5})
check("remove unknown", lambda: inv.remove_item(d, "kiwi", 1), exc=KeyError)
check("remove too much", lambda: inv.remove_item(d, "apple", 99), exc=ValueError)
check("remove returns same obj", lambda: inv.remove_item(d, "apple", 1) is d, True)
check("state after", lambda: d, {"apple": 4})

# total_value
inv_dict = {"apple": 4, "pear": 2, "kiwi": 7}
prices = {"apple": 1.5, "pear": 2.0}
check("total with missing price", lambda: inv.total_value(inv_dict, prices), 4 * 1.5 + 2 * 2.0)
check("total empty inv", lambda: inv.total_value({}, {}), 0)
check("total is float", lambda: isinstance(inv.total_value({}, {}), float), True)
check("total no prices", lambda: inv.total_value({"a": 3}, {}), 0)
check("total int prices", lambda: inv.total_value({"a": 3, "b": 1}, {"a": 2}), 6)
