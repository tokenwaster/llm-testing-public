"""Test script for inventory module."""

from inventory import add_item, remove_item, total_value

def test_add_item_accumulates():
    """Test that add_item accumulates with existing quantity."""
    inv = {}
    add_item(inv, "apple", 5)
    assert inv["apple"] == 5, f"Expected 5, got {inv['apple']}"
    
    # Accumulate
    add_item(inv, "apple", 3)
    assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"
    print("[PASS] add_item accumulates correctly")

def test_add_item_negative_qty():
    """Test that negative qty raises ValueError."""
    try:
        add_item({}, "apple", -1)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("[PASS] add_item raises ValueError for negative qty")

def test_remove_item_unknown_name():
    """Test that unknown name raises KeyError."""
    try:
        remove_item({}, "apple", 1)
        assert False, "Should have raised KeyError"
    except KeyError:
        print("[PASS] remove_item raises KeyError for unknown name")

def test_remove_item_not_enough():
    """Test that removing more than available raises ValueError."""
    inv = {"apple": 5}
    try:
        remove_item(inv, "apple", 10)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("[PASS] remove_item raises ValueError when not enough stock")

def test_remove_item_deletes_zero():
    """Test that item is deleted when quantity reaches 0."""
    inv = {"apple": 5}
    remove_item(inv, "apple", 5)
    assert "apple" not in inv, f"Expected 'apple' to be deleted, but got {inv}"
    print("[PASS] remove_item deletes item when quantity reaches 0")

def test_total_value_missing_price():
    """Test that items missing from prices count as 0."""
    inv = {"apple": 5, "banana": 3}
    prices = {"apple": 2.0}  # banana is missing
    result = total_value(inv, prices)
    expected = 5 * 2.0 + 3 * 0  # apple=10, banana=0
    assert result == expected, f"Expected {expected}, got {result}"
    print("[PASS] total_value counts missing prices as 0")

def test_total_value_normal():
    """Test normal total_value calculation."""
    inv = {"apple": 5, "banana": 3}
    prices = {"apple": 2.0, "banana": 1.5}
    result = total_value(inv, prices)
    expected = 5 * 2.0 + 3 * 1.5  # apple=10, banana=4.5
    assert result == expected, f"Expected {expected}, got {result}"
    print("[PASS] total_value calculates correctly with all prices")

if __name__ == "__main__":
    test_add_item_accumulates()
    test_add_item_negative_qty()
    test_remove_item_unknown_name()
    test_remove_item_not_enough()
    test_remove_item_deletes_zero()
    test_total_value_missing_price()
    test_total_value_normal()
