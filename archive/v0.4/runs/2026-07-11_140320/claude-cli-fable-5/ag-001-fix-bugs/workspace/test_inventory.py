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


def test_remove_partial():
    inv = {"apple": 5}
    remove_item(inv, "apple", 2)
    assert inv == {"apple": 3}


def test_remove_to_zero_deletes_key():
    inv = {"apple": 3}
    remove_item(inv, "apple", 3)
    assert "apple" not in inv


def test_remove_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        remove_item({}, "banana", 1)


def test_remove_too_many_raises_valueerror():
    with pytest.raises(ValueError):
        remove_item({"apple": 2}, "apple", 3)


def test_total_value():
    inv = {"apple": 2, "pear": 3}
    prices = {"apple": 1.5, "pear": 2.0}
    assert total_value(inv, prices) == 9.0


def test_total_value_missing_price_counts_as_zero():
    inv = {"apple": 2, "mystery": 10}
    prices = {"apple": 1.5}
    assert total_value(inv, prices) == 3.0
