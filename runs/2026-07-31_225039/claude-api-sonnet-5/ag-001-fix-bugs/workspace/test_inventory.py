
from inventory import add_item, remove_item, total_value

inv = {}
add_item(inv, "apple", 5)
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, inv

try:
    add_item(inv, "apple", -1)
    assert False
except ValueError:
    pass

remove_item(inv, "apple", 8)
assert inv == {}, inv

try:
    remove_item(inv, "banana", 1)
    assert False
except KeyError:
    pass

add_item(inv, "banana", 2)
try:
    remove_item(inv, "banana", 5)
    assert False
except ValueError:
    pass

prices = {"banana": 2.5}
assert total_value(inv, prices) == 5.0

add_item(inv, "cherry", 4)
assert total_value(inv, prices) == 5.0

print("all good")
