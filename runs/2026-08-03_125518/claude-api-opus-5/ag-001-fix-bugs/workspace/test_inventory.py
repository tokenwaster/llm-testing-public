from inventory import add_item, remove_item, total_value

inv = {}
add_item(inv, "apple", 3)
add_item(inv, "apple", 2)
assert inv == {"apple": 5}, inv
assert add_item(inv, "pear", 0) is inv
assert inv == {"apple": 5, "pear": 0}

try:
    add_item(inv, "apple", -1)
except ValueError:
    pass
else:
    raise AssertionError("no ValueError")

remove_item(inv, "apple", 2)
assert inv["apple"] == 3
remove_item(inv, "apple", 3)
assert "apple" not in inv, inv

try:
    remove_item(inv, "ghost", 1)
except KeyError:
    pass
else:
    raise AssertionError("no KeyError")

inv2 = {"a": 2}
try:
    remove_item(inv2, "a", 5)
except ValueError:
    pass
else:
    raise AssertionError("no ValueError")
assert inv2 == {"a": 2}

assert total_value({"a": 2, "b": 3}, {"a": 1.5, "b": 2}) == 9.0
assert total_value({"a": 2, "b": 3}, {"a": 1.5}) == 3.0
assert total_value({}, {}) == 0
print("all tests passed")
