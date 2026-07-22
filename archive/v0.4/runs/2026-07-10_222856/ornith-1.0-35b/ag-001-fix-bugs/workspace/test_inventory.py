"""Quick tests against the spec."""
from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {}
    add_item(inv, "apple", 5)
    assert inv == {"apple": 5}, inv
    add_item(inv, "apple", 3)
    assert inv == {"apple": 8}, inv  # should accumulate, not overwrite


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
    assert inv == {"apple": 2}, inv


def test_remove_item_unknown_raises_keyerror():
    inv = {}
    try:
        remove_item(inv, "banana", 1)
        assert False
    except KeyError:
        pass


def test_remove_item_too_much_raises_valueerror():
    inv = {"apple": 3}
    try:
        remove_item(inv, "apple", 5)
        assert False
    except ValueError:
        pass


def test_remove_item_zero_deletes_key():
    inv = {"apple": 3}
    remove_item(inv, "apple", 3)
    assert inv == {}, inv


def test_total_value_basic():
    inv = {"apple": 2, "banana": 3}
    prices = {"apple": 1.0, "banana": 0.5}
    assert total_value(inv, prices) == 2 * 1.0 + 3 * 0.5


def test_total_value_missing_price():
    inv = {"apple": 2, "mystery": 4}
    prices = {"apple": 1.0}
    # mystery is missing from prices; should count as 0
    assert total_value(inv, prices) == 2 * 1.0 + 0


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
        except AssertionError as e:
            print(f"FAIL: {t.__name__} -> {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {t.__name__} -> {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{failed} failure(s)")
