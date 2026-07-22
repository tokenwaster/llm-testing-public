"""Verify inventory.py matches its specification."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    add_item(inv, "apple", 5)
    assert inv == {"apple": 5}, inv
    add_item(inv, "apple", 3)
    assert inv == {"apple": 8}, inv

def test_add_item_negative_raises():
    try:
        add_item({}, "x", -1)
        assert False, "should have raised"
    except ValueError:
        pass


def test_remove_item_basic():
    inv = {"apple": 10}
    remove_item(inv, "apple", 3)
    assert inv == {"apple": 7}, inv

def test_remove_item_unknown_raises_keyerror():
    try:
        remove_item({}, "x", 1)
        assert False
    except KeyError:
        pass

def test_remove_item_too_much_raises_valueerror():
    try:
        remove_item({"apple": 2}, "apple", 5)
        assert False
    except ValueError:
        pass

def test_remove_item_zero_deletes_key():
    inv = {"apple": 3}
    remove_item(inv, "apple", 3)
    assert inv == {}, inv

def test_total_value_basic():
    inv = {"apple": 2, "banana": 5}
    prices = {"apple": 1.0, "banana": 0.5}
    assert total_value(inv, prices) == 4.5

def test_total_value_missing_price_counts_zero():
    inv = {"apple": 2}
    prices = {}  # apple not in prices
    assert total_value(inv, prices) == 0


test_add_item_accumulates()
test_add_item_negative_raises()
test_remove_item_basic()
test_remove_item_unknown_raises_keyerror()
test_remove_item_too_much_raises_valueerror()
test_remove_item_zero_deletes_key()
test_total_value_basic()
test_total_value_missing_price_counts_zero()
print("All tests passed.")
