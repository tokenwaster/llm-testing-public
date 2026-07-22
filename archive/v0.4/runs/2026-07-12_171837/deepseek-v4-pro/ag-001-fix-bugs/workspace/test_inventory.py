"""Quick tests for inventory.py"""
import inventory


def test_add_item():
    inv = {}
    # basic add
    inventory.add_item(inv, "apple", 5)
    assert inv == {"apple": 5}, f"basic add failed: {inv}"

    # accumulate
    inventory.add_item(inv, "apple", 3)
    assert inv == {"apple": 8}, f"accumulate failed: {inv}"

    # negative qty
    try:
        inventory.add_item(inv, "apple", -1)
        assert False, "should have raised ValueError"
    except ValueError:
        pass

    print("add_item: OK")


def test_remove_item():
    inv = {"apple": 10, "banana": 3}

    # normal remove
    inventory.remove_item(inv, "apple", 4)
    assert inv == {"apple": 6, "banana": 3}, f"remove failed: {inv}"

    # remove to exactly 0 -> delete key
    inventory.remove_item(inv, "banana", 3)
    assert inv == {"apple": 6}, f"remove-to-zero failed: {inv}"
    assert "banana" not in inv

    # unknown name
    try:
        inventory.remove_item(inv, "pear", 1)
        assert False, "should have raised KeyError"
    except KeyError:
        pass

    # too many
    try:
        inventory.remove_item(inv, "apple", 999)
        assert False, "should have raised ValueError"
    except ValueError:
        pass

    print("remove_item: OK")


def test_total_value():
    inv = {"apple": 2, "banana": 3}
    prices = {"apple": 1.5, "banana": 2.0}

    val = inventory.total_value(inv, prices)
    assert val == 2 * 1.5 + 3 * 2.0, f"total_value failed: {val}"

    # item missing from prices -> counts as 0
    inv2 = {"apple": 2, "kiwi": 5}
    val2 = inventory.total_value(inv2, prices)
    assert val2 == 2 * 1.5, f"missing price should be 0, got: {val2}"

    print("total_value: OK")


if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("All tests passed!")