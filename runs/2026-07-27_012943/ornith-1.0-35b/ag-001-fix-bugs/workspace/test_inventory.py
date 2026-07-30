"""Verify inventory.py matches spec."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    add_item(inv, "apple", 5)
    assert inv == {"apple": 5}
    add_item(inv, "apple", 3)
    assert inv == {"apple": 8}, f"Expected accumulation, got {inv}"


def test_add_item_negative_raises():
    try:
        add_item({}, "x", -1)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_remove_item_unknown_raises_keyerror():
    try:
        remove_item({}, "nope", 1)
        assert False
    except KeyError:
        pass


def test_remove_item_too_many_raises_valueerror():
    inv = {"x": 2}
    try:
        remove_item(inv, "x", 5)
        assert False
    except ValueError:
        pass


def test_remove_item_deletes_on_zero():
    inv = {"x": 3}
    remove_item(inv, "x", 3)
    assert inv == {}, f"Expected empty dict after reaching 0, got {inv}"


def test_total_value_missing_price_is_zero():
    inv = {"apple": 2, "mystery": 1}
    prices = {"apple": 1.5}
    assert total_value(inv, prices) == 3.0, f"Got {total_value(inv, prices)}"


def test_total_value_normal():
    inv = {"a": 3, "b": 2}
    prices = {"a": 1.0, "b": 5.0}
    assert total_value(inv, prices) == 13.0


if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_negative_raises()
    test_remove_item_unknown_raises_keyerror()
    test_remove_item_too_many_raises_valueerror()
    test_remove_item_deletes_on_zero()
    test_total_value_missing_price_is_zero()
    test_total_value_normal()
    print("All tests passed!")
