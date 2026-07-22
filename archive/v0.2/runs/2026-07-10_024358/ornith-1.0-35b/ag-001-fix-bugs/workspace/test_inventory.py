"""Quick smoke tests for inventory module."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    add_item(inv, "apple", 5)
    assert inv == {"apple": 5}, inv
    add_item(inv, "apple", 3)
    assert inv == {"apple": 8}, inv  # should accumulate, not overwrite


def test_add_item_negative_raises():
    try:
        add_item({}, "x", -1)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_remove_item_unknown_raises_keyerror():
    try:
        remove_item({}, "x", 1)
    except KeyError:
        return
    raise AssertionError("expected KeyError")


def test_remove_item_too_many_raises_valueerror():
    inv = {"apple": 3}
    try:
        remove_item(inv, "apple", 5)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_remove_item_deletes_on_zero():
    inv = {"apple": 2}
    remove_item(inv, "apple", 2)
    assert inv == {}, inv


def test_total_value_missing_price_counts_as_zero():
    inv = {"apple": 2, "mystery": 10}
    prices = {"apple": 3.5}
    assert total_value(inv, prices) == 7.0, total_value(inv, prices)


if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_negative_raises()
    test_remove_item_unknown_raises_keyerror()
    test_remove_item_too_many_raises_valueerror()
    test_remove_item_deletes_on_zero()
    test_total_value_missing_price_counts_as_zero()
    print("All tests passed.")
