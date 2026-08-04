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

remove_item(inv, "apple", 2)
assert inv == {"apple": 3}, inv
remove_item(inv, "apple", 3)
assert inv == {}, inv

try:
    remove_item(inv, "nope", 1)
    assert False
except KeyError:
    pass

add_item(inv, "banana", 2)
try:
    remove_item(inv, "banana", 5)
    assert False
except ValueError:
    pass

inv2 = {"apple": 2, "pear": 4}
assert total_value(inv2, {"apple": 1.5}) == 3.0, total_value(inv2, {"apple": 1.5})
assert total_value(inv2, {"apple": 1.5, "pear": 2}) == 11.0

print("all passed")
