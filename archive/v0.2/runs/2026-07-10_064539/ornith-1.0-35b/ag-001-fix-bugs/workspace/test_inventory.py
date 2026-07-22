"""Quick smoke tests for inventory module."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    assert add_item(inv, "apple", 5) is inv
    assert inv == {"apple": 5}
    add_item(inv, "apple", 3)
    assert inv["apple"] == 8

def test_add_item_negative_raises():
    try:
        add_item({}, "x", -1)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_remove_item_basic():
    inv = {"apple": 5}
    assert remove_item(inv, "apple", 3) is inv
    assert inv == {"apple": 2}

def test_remove_item_unknown_raises_keyerror():
    try:
        remove_item({}, "x", 1)
    except KeyError:
        return
    raise AssertionError("expected KeyError")

def test_remove_item_too_many_raises_valueerror():
    try:
        remove_item({"apple": 2}, "apple", 5)
    except ValueError:
        return
    raise AssertionError("expected ValueError")

def test_remove_item_zero_deletes_key():
    inv = {"apple": 1}
    remove_item(inv, "apple", 1)
    assert inv == {}


def test_total_value_basic():
    inv = {"apple": 2, "banana": 3}
    prices = {"apple": 1.0, "banana": 0.5}
    assert total_value(inv, prices) == 3.5

def test_total_value_missing_price_counts_zero():
    inv = {"apple": 2, "mystery": 4}
    prices = {"apple": 1.0}
    assert total_value(inv, prices) == 2.0


test_add_item_accumulates()
test_add_item_negative_raises()
test_remove_item_basic()
test_remove_item_unknown_raises_keyerror()
test_remove_item_too_many_raises_valueerror()
test_remove_item_zero_deletes_key()
test_total_value_basic()
test_total_value_missing_price_counts_zero()
print("All tests passed!")
