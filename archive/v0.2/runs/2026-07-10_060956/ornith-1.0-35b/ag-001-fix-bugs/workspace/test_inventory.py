"""Quick tests for inventory module."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    add_item(inv, "apple", 5)
    assert inv == {"apple": 5}
    add_item(inv, "apple", 3)
    assert inv == {"apple": 8}, f"got {inv}"


def test_add_item_negative_raises():
    inv = {}
    try:
        add_item(inv, "apple", -1)
        assert False, "should have raised"
    except ValueError:
        pass


def test_remove_item_basic():
    inv = {"apple": 5}
    remove_item(inv, "apple", 3)
    assert inv == {"apple": 2}, f"got {inv}"


def test_remove_item_zero_deletes_key():
    inv = {"apple": 5}
    remove_item(inv, "apple", 5)
    assert inv == {}, f"got {inv}"


def test_remove_item_unknown_raises_keyerror():
    inv = {}
    try:
        remove_item(inv, "apple", 1)
        assert False
    except KeyError:
        pass


def test_remove_item_too_many_raises_valueerror():
    inv = {"apple": 3}
    try:
        remove_item(inv, "apple", 5)
        assert False
    except ValueError:
        pass


def test_total_value_basic():
    inv = {"apple": 2, "banana": 3}
    prices = {"apple": 1.0, "banana": 0.5}
    assert total_value(inv, prices) == 3.5


def test_total_value_missing_price_counts_zero():
    inv = {"apple": 2, "mystery": 4}
    prices = {"apple": 1.0}
    assert total_value(inv, prices) == 2.0


if __name__ == "__main__":
    for name in [n for n in dir() if n.startswith("test_")]:
        fn = globals()[name]
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
        except Exception as e:
            print(f"ERROR {name}: {type(e).__name__}: {e}")
