#!/usr/bin/env python3
"""Test script for inventory module."""

from inventory import add_item, remove_item, total_value


def test_add_item_accumulates():
    inv = {"apple": 10}
    result = add_item(inv, "apple", 5)
    assert result["apple"] == 15, f"Expected 15 but got {result['apple']}"
    print("test_add_item_accumulates: PASSED")


def test_add_item_creates_new():
    inv = {}
    result = add_item(inv, "banana", 20)
    assert result["banana"] == 20, f"Expected 20 but got {result['banana']}"
    print("test_add_item_creates_new: PASSED")


def test_add_item_negative_raises():
    inv = {}
    try:
        add_item(inv, "cherry", -5)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"test_add_item_negative_raises: PASSED (raised {e})")


def test_remove_item_unknown_raises():
    inv = {"apple": 10}
    try:
        remove_item(inv, "banana", 5)
        assert False, "Should have raised KeyError"
    except KeyError as e:
        print(f"test_remove_item_unknown_raises: PASSED (raised {e})")


def test_remove_item_too_much_raises():
    inv = {"apple": 10}
    try:
        remove_item(inv, "apple", 20)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"test_remove_item_too_much_raises: PASSED (raised {e})")


def test_remove_item_deletes_at_zero():
    inv = {"apple": 10}
    result = remove_item(inv, "apple", 10)
    assert "apple" not in result, f"Key should be deleted but got {result}"
    print("test_remove_item_deletes_at_zero: PASSED")


def test_total_value_missing_price():
    inv = {"apple": 5}
    prices = {"banana": 2}
    total = total_value(inv, prices)
    assert total == 0, f"Expected 0 (missing price counts as 0) but got {total}"
    print("test_total_value_missing_price: PASSED")


def test_total_value_calculates_correct():
    inv = {"apple": 3, "banana": 2}
    prices = {"apple": 1.5, "banana": 2.0}
    total = total_value(inv, prices)
    assert total == 8.5, f"Expected 8.5 but got {total}"
    print("test_total_value_calculates_correct: PASSED")


if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_creates_new()
    test_add_item_negative_raises()
    test_remove_item_unknown_raises()
    test_remove_item_too_much_raises()
    test_remove_item_deletes_at_zero()
    test_total_value_missing_price()
    test_total_value_calculates_correct()
    print("\nAll tests passed!")
