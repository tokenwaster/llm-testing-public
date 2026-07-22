from inventory import add_item, remove_item, total_value

# add_item accumulates
inv = {}
add_item(inv, "apple", 5)
add_item(inv, "apple", 3)
assert inv == {"apple": 8}, inv

# add_item negative raises
try:
    add_item(inv, "apple", -1)
    assert False, "should raise ValueError"
except ValueError:
    pass

# remove_item unknown raises KeyError
try:
    remove_item(inv, "banana", 1)
    assert False, "should raise KeyError"
except KeyError:
    pass

# remove_item too much raises ValueError
try:
    remove_item(inv, "apple", 100)
    assert False, "should raise ValueError"
except ValueError:
    pass

# remove_item to zero deletes key
remove_item(inv, "apple", 8)
assert inv == {}, inv

# remove_item partial
inv = {"x": 10}
remove_item(inv, "x", 4)
assert inv == {"x": 6}, inv

# total_value missing prices count as 0
inv = {"a": 2, "b": 3, "c": 4}
prices = {"a": 1.5, "b": 2.0}  # c missing
assert total_value(inv, prices) == 2 * 1.5 + 3 * 2.0, total_value(inv, prices)

# total_value all missing
assert total_value({"z": 5}, {}) == 0

print("All tests passed.")
