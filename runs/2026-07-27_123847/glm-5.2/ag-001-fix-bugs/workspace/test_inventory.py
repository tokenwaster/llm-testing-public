import copy
import inventory


def test_add_item_accumulates():
    inv = {}
    inventory.add_item(inv, "apple", 5)
    inventory.add_item(inv, "apple", 3)
    assert inv == {"apple": 8}, inv


def test_add_item_negative():
    try:
        inventory.add_item({}, "apple", -1)
        assert False, "should have raised"
    except ValueError:
        pass


def test_remove_item_unknown():
    try:
        inventory.remove_item({}, "apple", 1)
        assert False, "should have raised"
    except KeyError:
        pass


def test_remove_item_too_many():
    inv = {"apple": 5}
    try:
        inventory.remove_item(inv, "apple", 6)
        assert False, "should have raised"
    except ValueError:
        pass
    assert inv == {"apple": 5}, inv


def test_remove_item_zero_deletes():
    inv = {"apple": 5}
    inventory.remove_item(inv, "apple", 5)
    assert inv == {}, inv


def test_total_value_missing_price():
    inv = {"apple": 5, "banana": 3}
    prices = {"apple": 2}
    assert inventory.total_value(inv, prices) == 10


def test_total_value_all():
    inv = {"apple": 5, "banana": 3}
    prices = {"apple": 2, "banana": 4}
    assert inventory.total_value(inv, prices) == 22


if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_negative()
    test_remove_item_unknown()
    test_remove_item_too_many()
    test_remove_item_zero_deletes()
    test_total_value_missing_price()
    test_total_value_all()
    print("All tests passed.")
