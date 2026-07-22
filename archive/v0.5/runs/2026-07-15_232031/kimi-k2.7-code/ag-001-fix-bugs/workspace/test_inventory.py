import pytest
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    add_item(inv, "apple", 5)
    add_item(inv, "apple", 3)
    assert inv == {"apple": 8}


def test_add_item_negative_qty_raises():
    inv = {"apple": 5}
    with pytest.raises(ValueError):
        add_item(inv, "apple", -1)


def test_remove_item_unknown_raises():
    inv = {}
    with pytest.raises(KeyError):
        remove_item(inv, "apple", 1)


def test_remove_item_too_many_raises():
    inv = {"apple": 5}
    with pytest.raises(ValueError):
        remove_item(inv, "apple", 6)


def test_remove_item_zero_deletes():
    inv = {"apple": 5}
    remove_item(inv, "apple", 5)
    assert inv == {}


def test_total_value_missing_price_counts_zero():
    inv = {"apple": 5, "banana": 2}
    prices = {"apple": 1.0}
    assert total_value(inv, prices) == 5.0


def test_total_value_empty_inventory():
    assert total_value({}, {"apple": 1.0}) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
