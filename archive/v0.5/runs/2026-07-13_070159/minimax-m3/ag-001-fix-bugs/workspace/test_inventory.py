"""Tests for inventory.py spec compliance."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    add_item(inv, "apple", 3)
    add_item(inv, "apple", 5)
    assert inv == {"apple": 8}, f"expected {{'apple': 8}}, got {inv}"
    print("test_add_item_accumulates: PASS")


def test_add_item_returns_inventory():
    inv = {}
    result = add_item(inv, "apple", 3)
    assert result is inv, "add_item should return the inventory"
    print("test_add_item_returns_inventory: PASS")


def test_add_item_negative_raises():
    inv = {}
    try:
        add_item(inv, "apple", -1)
    except ValueError:
        print("test_add_item_negative_raises: PASS")
    else:
        raise AssertionError("expected ValueError for negative qty")


def test_remove_item_basic():
    inv = {"apple": 5}
    remove_item(inv, "apple", 3)
    assert inv == {"apple": 2}, f"expected {{'apple': 2}}, got {inv}"
    print("test_remove_item_basic: PASS")


def test_remove_item_to_zero_deletes_key():
    inv = {"apple": 5}
    remove_item(inv, "apple", 5)
    assert inv == {}, f"expected empty dict, got {inv}"
    assert "apple" not in inv, "key should be deleted when qty reaches 0"
    print("test_remove_item_to_zero_deletes_key: PASS")


def test_remove_item_unknown_raises_keyerror():
    inv = {"apple": 5}
    try:
        remove_item(inv, "banana", 1)
    except KeyError:
        print("test_remove_item_unknown_raises_keyerror: PASS")
    else:
        raise AssertionError("expected KeyError for unknown name")


def test_remove_item_too_much_raises_valueerror():
    inv = {"apple": 3}
    try:
        remove_item(inv, "apple", 5)
    except ValueError:
        print("test_remove_item_too_much_raises_valueerror: PASS")
    else:
        raise AssertionError("expected ValueError for removing too much")


def test_remove_item_returns_inventory():
    inv = {"apple": 5}
    result = remove_item(inv, "apple", 2)
    assert result is inv, "remove_item should return the inventory"
    print("test_remove_item_returns_inventory: PASS")


def test_total_value_basic():
    inv = {"apple": 3, "banana": 2}
    prices = {"apple": 1.50, "banana": 0.75}
    expected = 3 * 1.50 + 2 * 0.75  # 6.0
    result = total_value(inv, prices)
    assert abs(result - expected) < 1e-9, f"expected {expected}, got {result}"
    print("test_total_value_basic: PASS")


def test_total_value_missing_price_is_zero():
    inv = {"apple": 3, "banana": 2}
    prices = {"apple": 1.50}  # banana missing
    expected = 3 * 1.50  # 4.5, banana counts as 0
    result = total_value(inv, prices)
    assert abs(result - expected) < 1e-9, f"expected {expected}, got {result}"
    print("test_total_value_missing_price_is_zero: PASS")


def test_total_value_empty_inventory():
    inv = {}
    prices = {"apple": 1.50}
    assert total_value(inv, prices) == 0
    print("test_total_value_empty_inventory: PASS")


def test_total_value_returns_float():
    inv = {"apple": 2}
    prices = {"apple": 1}
    result = total_value(inv, prices)
    assert isinstance(result, float), f"expected float, got {type(result)}"
    print("test_total_value_returns_float: PASS")


if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_returns_inventory()
    test_add_item_negative_raises()
    test_remove_item_basic()
    test_remove_item_to_zero_deletes_key()
    test_remove_item_unknown_raises_keyerror()
    test_remove_item_too_much_raises_valueerror()
    test_remove_item_returns_inventory()
    test_total_value_basic()
    test_total_value_missing_price_is_zero()
    test_total_value_empty_inventory()
    test_total_value_returns_float()
    print("\nAll tests passed!")
