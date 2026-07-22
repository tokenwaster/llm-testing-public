"""ag-001 checker. Redesigned so a no-op (unedited seed) scores ~0, a correct
fix scores 1.0, and a partial fix scores in between: nearly every test depends
on one of the two bugs (add_item must ACCUMULATE; total_value treats a missing
price as 0). A few error-path guards catch a rewrite that breaks working code."""
import pytest

from inventory import add_item, remove_item, total_value


def test_add_accumulates():
    inv = {}
    add_item(inv, "bolt", 5)
    add_item(inv, "bolt", 3)
    assert inv == {"bolt": 8}


def test_add_accumulates_repeatedly():
    inv = {}
    for q in (2, 3, 5):
        add_item(inv, "nut", q)
    assert inv == {"nut": 10}


def test_add_accumulates_per_item():
    inv = {}
    add_item(inv, "bolt", 4)
    add_item(inv, "nut", 2)
    add_item(inv, "bolt", 6)
    assert inv == {"bolt": 10, "nut": 2}


def test_add_then_remove_uses_accumulated_total():
    inv = {}
    add_item(inv, "bolt", 5)
    add_item(inv, "bolt", 5)
    remove_item(inv, "bolt", 3)
    assert inv == {"bolt": 7}


def test_remove_to_zero_deletes_key():
    inv = {}
    add_item(inv, "bolt", 1)
    add_item(inv, "bolt", 1)
    remove_item(inv, "bolt", 2)
    assert "bolt" not in inv


def test_total_missing_price_counts_zero():
    assert total_value({"bolt": 4, "mystery": 10}, {"bolt": 0.5}) == 2.0


def test_total_all_prices_missing_is_zero():
    assert total_value({"a": 3, "b": 7}, {}) == 0.0


def test_total_mixed_present_and_missing():
    v = total_value({"bolt": 4, "nut": 2, "ghost": 100},
                    {"bolt": 0.5, "nut": 0.25})
    assert v == 2.5


def test_total_after_accumulate_and_missing():
    inv = {}
    add_item(inv, "bolt", 2)
    add_item(inv, "bolt", 2)
    assert total_value(inv, {}) == 0.0
    assert total_value(inv, {"bolt": 2.0}) == 8.0


def test_add_negative_raises():
    with pytest.raises(ValueError):
        add_item({}, "bolt", -1)


def test_remove_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        remove_item({}, "ghost", 1)


def test_remove_too_many_raises():
    with pytest.raises(ValueError):
        remove_item({"bolt": 2}, "bolt", 3)
