"""Quick tests against the spec."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {"apples": 5}
    add_item(inv, "apples", 3)
    assert inv["apples"] == 8, f"Expected 8, got {inv['apples']}"

    # New item starts at qty
    add_item(inv, "bananas", 10)
    assert inv["bananas"] == 10


def test_add_item_negative_raises():
    try:
        add_item({}, "x", -1)
        assert False, "Should have raised"
    except ValueError:
        pass


def test_remove_item_unknown_raises_keyerror():
    try:
        remove_item({}, "nope", 1)
        assert False
    except KeyError:
        pass


def test_remove_item_too_much_raises_valueerror():
    inv = {"x": 3}
    try:
        remove_item(inv, "x", 5)
        assert False
    except ValueError:
        pass


def test_remove_item_zero_deletes_key():
    inv = {"x": 2}
    remove_item(inv, "x", 2)
    assert "x" not in inv


def test_total_value_missing_price_counts_as_0():
    inv = {"a": 10, "b": 5}
    prices = {"a": 2.0}
    assert total_value(inv, prices) == 20.0, f"got {total_value(inv, prices)}"


def test_total_value_normal():
    inv = {"a": 3, "b": 4}
    prices = {"a": 1.5, "b": 2.0}
    assert total_value(inv, prices) == 3 * 1.5 + 4 * 2.0


if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_negative_raises()
    test_remove_item_unknown_raises_keyerror()
    test_remove_item_too_much_raises_valueerror()
    test_remove_item_zero_deletes_key()
    test_total_value_missing_price_counts_as_0()
    test_total_value_normal()
    print("All tests passed!")
