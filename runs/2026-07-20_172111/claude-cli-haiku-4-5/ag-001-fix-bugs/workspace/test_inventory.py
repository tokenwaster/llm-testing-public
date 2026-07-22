"""Test inventory.py against the specification."""

from inventory import add_item, remove_item, total_value

def test_add_item_accumulates():
    """add_item should accumulate with existing quantity."""
    inv = {"apple": 5}
    result = add_item(inv, "apple", 3)
    assert result["apple"] == 8, f"Expected 8, got {result['apple']}"
    print("OK: add_item accumulates")

def test_add_item_new():
    """add_item should add new items."""
    inv = {}
    result = add_item(inv, "banana", 2)
    assert result["banana"] == 2
    print("OK: add_item adds new items")

def test_add_item_negative():
    """add_item should raise ValueError for negative qty."""
    inv = {}
    try:
        add_item(inv, "apple", -1)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("OK: add_item rejects negative qty")

def test_remove_item_basic():
    """remove_item should remove qty."""
    inv = {"apple": 5}
    result = remove_item(inv, "apple", 2)
    assert result["apple"] == 3
    print("OK: remove_item removes qty")

def test_remove_item_deletes_zero():
    """remove_item should delete key when qty reaches 0."""
    inv = {"apple": 2}
    result = remove_item(inv, "apple", 2)
    assert "apple" not in result
    print("OK: remove_item deletes at zero")

def test_remove_item_unknown():
    """remove_item should raise KeyError for unknown name."""
    inv = {}
    try:
        remove_item(inv, "apple", 1)
        assert False, "Should have raised KeyError"
    except KeyError:
        print("OK: remove_item raises KeyError for unknown item")

def test_remove_item_excess():
    """remove_item should raise ValueError for excess removal."""
    inv = {"apple": 2}
    try:
        remove_item(inv, "apple", 5)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("OK: remove_item raises ValueError for excess removal")

def test_total_value_basic():
    """total_value should sum quantity x price."""
    inv = {"apple": 2, "banana": 3}
    prices = {"apple": 1.5, "banana": 0.5}
    result = total_value(inv, prices)
    expected = 2 * 1.5 + 3 * 0.5
    assert result == expected, f"Expected {expected}, got {result}"
    print("OK: total_value sums correctly")

def test_total_value_missing_price():
    """total_value should treat missing prices as 0."""
    inv = {"apple": 2, "banana": 3}
    prices = {"apple": 1.5}  # banana is missing
    result = total_value(inv, prices)
    expected = 2 * 1.5  # banana counts as 0
    assert result == expected, f"Expected {expected}, got {result}"
    print("OK: total_value treats missing prices as 0")

if __name__ == "__main__":
    try:
        test_add_item_accumulates()
    except AssertionError as e:
        print(f"FAIL test_add_item_accumulates: {e}")

    test_add_item_new()
    test_add_item_negative()

    try:
        test_remove_item_basic()
    except AssertionError as e:
        print(f"FAIL test_remove_item_basic: {e}")

    test_remove_item_deletes_zero()
    test_remove_item_unknown()
    test_remove_item_excess()

    try:
        test_total_value_basic()
    except AssertionError as e:
        print(f"FAIL test_total_value_basic: {e}")

    try:
        test_total_value_missing_price()
    except AssertionError as e:
        print(f"FAIL test_total_value_missing_price: {e}")
