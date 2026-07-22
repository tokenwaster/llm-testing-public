"""Quick smoke tests for inventory module."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    assert add_item(inv, "apple", 5) == {"apple": 5}
    assert add_item(inv, "apple", 3) == {"apple": 8}, f"got {inv}"
    print("add_item accumulates: OK")


def test_add_item_negative_raises():
    inv = {}
    try:
        add_item(inv, "x", -1)
    except ValueError:
        print("add_item negative raises ValueError: OK")
        return
    raise AssertionError("should have raised ValueError")


def test_remove_item_basic():
    inv = {"apple": 10}
    assert remove_item(inv, "apple", 3) == {"apple": 7}
    print("remove_item basic: OK")


def test_remove_item_unknown_raises_keyerror():
    inv = {}
    try:
        remove_item(inv, "x", 1)
    except KeyError:
        print("remove_item unknown raises KeyError: OK")
        return
    raise AssertionError("should have raised KeyError")


def test_remove_item_too_many_raises_valueerror():
    inv = {"apple": 2}
    try:
        remove_item(inv, "apple", 5)
    except ValueError:
        print("remove_item too many raises ValueError: OK")
        return
    raise AssertionError("should have raised ValueError")


def test_remove_item_zero_deletes_key():
    inv = {"apple": 2}
    assert remove_item(inv, "apple", 2) == {}
    assert "apple" not in inv
    print("remove_item zero deletes key: OK")


def test_total_value_basic():
    inv = {"apple": 3, "banana": 5}
    prices = {"apple": 1.0, "banana": 0.5}
    assert total_value(inv, prices) == 5.5, f"got {total_value(inv, prices)}"
    print("total_value basic: OK")


def test_total_value_missing_price():
    inv = {"apple": 3, "mystery": 2}
    prices = {"apple": 1.0}
    assert total_value(inv, prices) == 3.0, f"got {total_value(inv, prices)}"
    print("total_value missing price counts as 0: OK")


if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_negative_raises()
    test_remove_item_basic()
    test_remove_item_unknown_raises_keyerror()
    test_remove_item_too_many_raises_valueerror()
    test_remove_item_zero_deletes_key()
    test_total_value_basic()
    test_total_value_missing_price()
    print("\nAll tests passed!")
