"""Quick tests against the spec."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    add_item(inv, "apple", 5)
    assert inv == {"apple": 5}, inv
    add_item(inv, "apple", 3)
    assert inv == {"apple": 8}, inv  # should accumulate


def test_add_item_negative_raises():
    inv = {}
    try:
        add_item(inv, "apple", -1)
        assert False, "should have raised"
    except ValueError:
        pass


def test_remove_item_basic():
    inv = {"apple": 5}
    remove_item(inv, "apple", 3)
    assert inv == {"apple": 2}, inv


def test_remove_item_unknown_raises_keyerror():
    inv = {}
    try:
        remove_item(inv, "banana", 1)
        assert False
    except KeyError:
        pass


def test_remove_item_too_many_raises_valueerror():
    inv = {"apple": 2}
    try:
        remove_item(inv, "apple", 5)
        assert False
    except ValueError:
        pass


def test_remove_item_zero_deletes_key():
    inv = {"apple": 2}
    remove_item(inv, "apple", 2)
    assert inv == {}, inv


def test_total_value_missing_price_counts_as_0():
    inv = {"apple": 3, "banana": 2}
    prices = {"apple": 1.5}
    result = total_value(inv, prices)
    assert result == 4.5, result  # banana missing -> 0


if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_negative_raises()
    test_remove_item_basic()
    test_remove_item_unknown_raises_keyerror()
    test_remove_item_too_many_raises_valueerror()
    test_remove_item_zero_deletes_key()
    test_total_value_missing_price_counts_as_0()
    print("All tests passed!")
