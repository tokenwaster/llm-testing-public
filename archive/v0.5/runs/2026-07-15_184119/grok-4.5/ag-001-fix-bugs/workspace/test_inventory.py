import inventory as inv

# add_item accumulates
d = {}
inv.add_item(d, "apple", 3)
inv.add_item(d, "apple", 2)
assert d == {"apple": 5}, d

# add_item rejects negative
try:
    inv.add_item(d, "apple", -1)
    assert False, "should raise"
except ValueError:
    pass

# remove_item
inv.remove_item(d, "apple", 2)
assert d == {"apple": 3}
inv.remove_item(d, "apple", 3)
assert d == {}

# remove unknown
try:
    inv.remove_item(d, "pear", 1)
    assert False
except KeyError:
    pass

# remove too many
inv.add_item(d, "apple", 2)
try:
    inv.remove_item(d, "apple", 5)
    assert False
except ValueError:
    pass

# total_value missing prices count as 0
d = {"apple": 2, "banana": 3}
assert inv.total_value(d, {"apple": 1.5}) == 3.0
assert inv.total_value(d, {"apple": 1.5, "banana": 2.0}) == 9.0
assert isinstance(inv.total_value(d, {}), float)

print("all tests passed")
