"""Tests for inventory.py."""

from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    add_item(inv, "apple", 3)
    add_item(inv, "apple", 2)
    assert inv == {"apple": 5}


def test_add_item_negative_raises():
    inv = {}
    try:
        add_item(inv, "apple", -1)
        assert False, "should have raised"
    except ValueError:
        pass


def test_add_item_returns_inventory():
    inv = {}
    assert add_item(inv, "apple", 1) is inv


def test_remove_item_unknown_raises():
    inv = {"apple": 1}
    try:
        remove_item(inv, "banana", 1)
        assert False, "should have raised KeyError"
    except KeyError:
        pass


def test_remove_item_too_many_raises():
    inv = {"apple": 2}
    try:
        remove_item(inv, "apple", 3)
        assert False, "should have raised ValueError"
    except ValueError:
        pass


def test_remove_item_deletes_zero():
    inv = {"apple": 2}
    remove_item(inv, "apple", 2)
    assert "apple" not in inv


def test_remove_item_partial():
    inv = {"apple": 5}
    remove_item(inv, "apple", 3)
    assert inv == {"apple": 2}


def test_remove_item_returns_inventory():
    inv = {"apple": 1}
    assert remove_item(inv, "apple", 1) is inv


def test_total_value_missing_price_counts_zero():
    inv = {"apple": 2, "banana": 3}
    prices = {"apple": 10}
    assert total_value(inv, prices) == 20


def test_total_value_all_present():
    inv = {"apple": 2, "banana": 3}
    prices = {"apple": 10, "banana": 5}
    assert total_value(inv, prices) == 35


if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_negative_raises()
    test_add_item_returns_inventory()
    test_remove_item_unknown_raises()
    test_remove_item_too_many_raises()
    test_remove_item_deletes_zero()
    test_remove_item_partial()
    test_remove_item_returns_inventory()
    test_total_value_missing_price_counts_zero()
    test_total_value_all_present()
    print("All tests passed.")
