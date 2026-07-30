from inventory import add_item, remove_item, total_value

# add_item: accumulation
inv = {}
add_item(inv, "apple", 3)
add_item(inv, "apple", 2)
assert inv == {"apple": 5}, f"accumulation failed: {inv}"
print("add_item accumulation OK")

# add_item: new item
add_item(inv, "banana", 1)
assert inv == {"apple": 5, "banana": 1}, f"new item failed: {inv}"
print("add_item new item OK")

# add_item: negative qty raises ValueError
try:
    add_item(inv, "apple", -1)
    assert False, "should have raised"
except ValueError:
    print("add_item negative qty OK")

# add_item: returns inventory
ret = add_item({}, "x", 1)
assert ret == {"x": 1}
print("add_item return value OK")

# remove_item: unknown name raises KeyError
try:
    remove_item({}, "ghost", 1)
    assert False, "should have raised"
except KeyError:
    print("remove_item unknown KeyError OK")

# remove_item: too much raises ValueError
try:
    remove_item({"a": 2}, "a", 5)
    assert False, "should have raised"
except ValueError:
    print("remove_item over ValueError OK")

# remove_item: normal
remove_item(inv, "apple", 2)
assert inv == {"apple": 3, "banana": 1}, f"normal remove failed: {inv}"
print("remove_item normal OK")

# remove_item: key deleted at 0
remove_item(inv, "banana", 1)
assert inv == {"apple": 3}, f"key delete failed: {inv}"
print("remove_item delete at 0 OK")

# total_value
inv = {"a": 2, "b": 3, "c": 1}
prices = {"a": 1.5, "b": 2.0}
# a: 3.0, b: 6.0, c: 0  -> 9.0
assert total_value(inv, prices) == 9.0, f"total_value failed: {total_value(inv, prices)}"
print("total_value with missing price OK")

assert total_value({}, {}) == 0.0
print("total_value empty OK")

# total_value with float return type
result = total_value({"a": 1}, {"a": 1.5})
assert isinstance(result, float), f"expected float, got {type(result)}"
print("total_value return type float OK")

print("\nAll tests passed!")
