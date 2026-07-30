from inventory import add_item, remove_item, total_value

inv = {}
add_item(inv, "apple", 3)
add_item(inv, "apple", 2)
assert inv == {"apple": 5}, inv

try:
    add_item(inv, "x", -1)
    assert False
except ValueError:
    pass

remove_item(inv, "apple", 5)
assert inv == {}, inv

inv = {"a": 2, "b": 3}
try:
    remove_item(inv, "missing", 1)
    assert False
except KeyError:
    pass

try:
    remove_item(inv, "a", 5)
    assert False
except ValueError:
    pass

remove_item(inv, "a", 1)
assert inv == {"a": 1, "b": 3}

val = total_value({"a": 2, "b": 3}, {"a": 1.5})
assert val == 3.0, val

val = total_value({}, {})
assert val == 0

print("all passed")
