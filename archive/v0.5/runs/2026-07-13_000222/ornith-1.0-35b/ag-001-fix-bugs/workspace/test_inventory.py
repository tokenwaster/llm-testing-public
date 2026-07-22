"""Quick tests against the spec."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {"apple": 5}
    add_item(inv, "apple", 3)
    assert inv["apple"] == 8, f"expected 8, got {inv['apple']}"

    # new item starts at qty
    add_item(inv, "banana", 10)
    assert inv["banana"] == 10

    # negative raises ValueError
    try:
        add_item(inv, "x", -1)
        assert False, "should have raised"
    except ValueError:
        pass


def test_remove_item():
    inv = {"apple": 5}
    remove_item(inv, "apple", 3)
    assert inv["apple"] == 2

    # depletes and deletes key
    remove_item(inv, "apple", 2)
    assert "apple" not in inv

    # unknown raises KeyError
    try:
        remove_item(inv, "mango", 1)
        assert False
    except KeyError:
        pass

    # over-removing raises ValueError
    inv = {"apple": 2}
    try:
        remove_item(inv, "apple", 5)
        assert False
    except ValueError:
        pass


def test_total_value_missing_prices():
    inv = {"apple": 3, "mango": 2}
    prices = {"apple": 1.5}
    # mango missing from prices -> counts as 0
    assert total_value(inv, prices) == 4.5, f"got {total_value(inv, prices)}"


if __name__ == "__main__":
    test_add_item_accumulates()
    test_remove_item()
    test_total_value_missing_prices()
    print("All tests passed.")
