"""Quick tests for inventory module."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    assert add_item(inv, "apple", 5) == {"apple": 5}
    assert add_item(inv, "apple", 3) == {"apple": 8}, f"got {inv}"
    print("PASS: add_item accumulates")


def test_add_item_negative_raises():
    inv = {}
    try:
        add_item(inv, "apple", -1)
        assert False, "should have raised"
    except ValueError:
        pass
    print("PASS: add_item raises on negative qty")


def test_remove_item_basic():
    inv = {"apple": 5}
    assert remove_item(inv, "apple", 3) == {"apple": 2}, f"got {inv}"
    print("PASS: remove_item basic")


def test_remove_item_deletes_on_zero():
    inv = {"apple": 3}
    assert remove_item(inv, "apple", 3) == {}, f"got {inv}"
    print("PASS: remove_item deletes on zero")


def test_remove_item_unknown_raises_keyerror():
    inv = {}
    try:
        remove_item(inv, "apple", 1)
        assert False
    except KeyError:
        pass
    print("PASS: remove_item raises KeyError for unknown name")


def test_remove_item_too_many_raises_valueerror():
    inv = {"apple": 2}
    try:
        remove_item(inv, "apple", 5)
        assert False
    except ValueError:
        pass
    print("PASS: remove_item raises ValueError when removing too many")


def test_total_value_basic():
    inv = {"apple": 3, "banana": 2}
    prices = {"apple": 1.0, "banana": 0.5}
    assert total_value(inv, prices) == 4.0, f"got {total_value(inv, prices)}"
    print("PASS: total_value basic")


def test_total_value_missing_price():
    inv = {"apple": 3, "mystery": 2}
    prices = {"apple": 1.0}
    assert total_value(inv, prices) == 3.0, f"got {total_value(inv, prices)}"
    print("PASS: total_value treats missing price as 0")


if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_negative_raises()
    test_remove_item_basic()
    test_remove_item_deletes_on_zero()
    test_remove_item_unknown_raises_keyerror()
    test_remove_item_too_many_raises_valueerror()
    test_total_value_basic()
    test_total_value_missing_price()
    print("\nAll tests passed!")
