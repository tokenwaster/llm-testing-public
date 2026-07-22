"""Quick tests against the spec."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {"apple": 5}
    add_item(inv, "apple", 3)
    assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"

    # new item starts at qty
    add_item(inv, "banana", 10)
    assert inv["banana"] == 10

    # negative raises ValueError
    try:
        add_item(inv, "x", -1)
        assert False, "Should have raised"
    except ValueError:
        pass


def test_remove_item():
    inv = {"apple": 5}
    remove_item(inv, "apple", 3)
    assert inv == {"apple": 2}, f"Got {inv}"

    # removing all -> key deleted
    remove_item(inv, "apple", 2)
    assert inv == {}, f"Expected empty, got {inv}"

    # unknown name raises KeyError
    try:
        remove_item({}, "x", 1)
        assert False
    except KeyError:
        pass

    # removing more than available raises ValueError
    inv = {"apple": 2}
    try:
        remove_item(inv, "apple", 5)
        assert False
    except ValueError:
        pass


def test_total_value_missing_prices():
    inv = {"apple": 2, "banana": 3}
    prices = {"apple": 1.5}
    # banana missing from prices -> counts as 0
    assert total_value(inv, prices) == 3.0, f"Got {total_value(inv, prices)}"


if __name__ == "__main__":
    test_add_item_accumulates()
    print("test_add_item_accumulates OK")
    test_remove_item()
    print("test_remove_item OK")
    test_total_value_missing_prices()
    print("test_total_value_missing_prices OK")
