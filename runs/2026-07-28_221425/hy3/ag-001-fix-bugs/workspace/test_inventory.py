from inventory import add_item, remove_item, total_value

# add_item should accumulate
inv = {}
add_item(inv, "apple", 5)
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, inv

# negative qty raises
try:
    add_item({}, "x", -1)
    assert False
except ValueError:
    pass

# remove_item unknown raises KeyError
try:
    remove_item({}, "x", 1)
    assert False
except KeyError:
    pass

# remove more than stock raises ValueError
try:
    remove_item({"x": 2}, "x", 3)
    assert False
except ValueError:
    pass

# removes and deletes at zero
inv = {"x": 2}
remove_item(inv, "x", 2)
assert inv == {}, inv

# total_value missing price -> 0
inv = {"a": 2, "b": 1}
prices = {"a": 5}
assert total_value(inv, prices) == 10, total_value(inv, prices)

print("ALL TESTS PASSED")
