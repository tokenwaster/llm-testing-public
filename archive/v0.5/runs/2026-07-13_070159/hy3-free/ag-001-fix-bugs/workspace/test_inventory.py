from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    add_item(inv, "a", 3)
    add_item(inv, "a", 2)
    assert inv == {"a": 5}, inv
    # negative qty
    try:
        add_item({}, "a", -1)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_remove_item():
    inv = {"a": 5}
    remove_item(inv, "a", 2)
    assert inv == {"a": 3}, inv
    # remove to zero deletes key
    remove_item(inv, "a", 3)
    assert inv == {}, inv
    # unknown name
    try:
        remove_item({}, "x", 1)
        assert False, "expected KeyError"
    except KeyError:
        pass
    # too many
    try:
        remove_item({"a": 1}, "a", 2)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_total_value():
    inv = {"a": 2, "b": 3, "c": 1}
    prices = {"a": 10, "b": 5}  # c missing
    assert total_value(inv, prices) == 2 * 10 + 3 * 5 + 1 * 0, total_value(inv, prices)


test_add_item_accumulates()
test_remove_item()
test_total_value()
print("All tests passed")
