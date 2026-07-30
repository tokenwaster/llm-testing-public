import pytest
from inventory import add_item, remove_item, total_value


def test_add_accumulates():
    inv = {}
    add_item(inv, "apple", 3)
    add_item(inv, "apple", 2)
    assert inv == {"apple": 5}


def test_add_negative_raises():
    with pytest.raises(ValueError):
        add_item({}, "apple", -1)


def test_add_returns_inventory():
    inv = {}
    assert add_item(inv, "x", 1) is inv


def test_remove_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        remove_item({}, "apple", 1)


def test_remove_too_many_raises_valueerror():
    with pytest.raises(ValueError):
        remove_item({"apple": 2}, "apple", 3)


def test_remove_to_zero_deletes_key():
    inv = {"apple": 2}
    remove_item(inv, "apple", 2)
    assert "apple" not in inv


def test_remove_partial():
    inv = {"apple": 5}
    remove_item(inv, "apple", 2)
    assert inv == {"apple": 3}


def test_total_value():
    assert total_value({"a": 2, "b": 3}, {"a": 1.5, "b": 2.0}) == 9.0


def test_total_value_missing_price_counts_zero():
    assert total_value({"a": 2, "b": 3}, {"a": 1.5}) == 3.0


def test_total_value_empty():
    assert total_value({}, {}) == 0
