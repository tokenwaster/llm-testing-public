import pytest

from inventory import add_item, remove_item, total_value


def test_add_accumulates():
    inv = {}
    add_item(inv, "bolt", 5)
    add_item(inv, "bolt", 3)
    assert inv == {"bolt": 8}


def test_add_negative_raises():
    with pytest.raises(ValueError):
        add_item({}, "bolt", -1)


def test_remove_basic():
    inv = {"bolt": 8}
    remove_item(inv, "bolt", 3)
    assert inv == {"bolt": 5}


def test_remove_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        remove_item({}, "ghost", 1)


def test_remove_too_many_raises():
    with pytest.raises(ValueError):
        remove_item({"bolt": 2}, "bolt", 3)


def test_remove_to_zero_deletes_key():
    inv = {"bolt": 2}
    remove_item(inv, "bolt", 2)
    assert "bolt" not in inv


def test_total_value():
    assert total_value({"bolt": 4, "nut": 2}, {"bolt": 0.5, "nut": 0.25}) == 2.5


def test_total_value_missing_price_counts_zero():
    assert total_value({"bolt": 4, "mystery": 10}, {"bolt": 0.5}) == 2.0
