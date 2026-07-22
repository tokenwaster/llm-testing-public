#!/usr/bin/env python3
"""Comprehensive test for inventory module."""

from inventory import add_item, remove_item, total_value

def test_add_item():
    """Test add_item function."""
    inv = {}
    
    # Test adding new item
    result = add_item(inv, "apple", 10)
    assert result == {"apple": 10}, f"Expected {{'apple': 10}}, got {result}"
    assert inv == {"apple": 10}, "Inventory should be modified in place"
    
    # Test accumulating existing item
    result = add_item(inv, "apple", 5)
    assert result == {"apple": 15}, f"Expected {{'apple': 15}}, got {result}"
    
    # Test adding different item
    result = add_item(inv, "banana", 3)
    assert result == {"apple": 15, "banana": 3}, f"Expected {{'apple': 15, 'banana': 3}}, got {result}"
    
    # Test negative quantity
    try:
        add_item(inv, "orange", -2)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "qty must be non-negative"
    
    print("All add_item tests passed")


def test_remove_item():
    """Test remove_item function."""
    inv = {"apple": 10, "banana": 5}
    
    # Test removing from existing item
    result = remove_item(inv, "apple", 3)
    assert result == {"apple": 7, "banana": 5}, f"Expected {{'apple': 7, 'banana': 5}}, got {result}"
    
    # Test removing to zero (should delete key)
    result = remove_item(inv, "banana", 5)
    assert result == {"apple": 7}, f"Expected {{'apple': 7}}, got {result}"
    assert "banana" not in inv
    
    # Test unknown item
    try:
        remove_item(inv, "orange", 2)
        assert False, "Should have raised KeyError"
    except KeyError as e:
        assert str(e) == "'orange'"
    
    # Test insufficient stock
    try:
        remove_item(inv, "apple", 10)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "not enough stock"
    
    print("All remove_item tests passed")


def test_total_value():
    """Test total_value function."""
    inv = {"apple": 10, "banana": 5, "orange": 3}
    prices = {"apple": 0.5, "banana": 0.3}
    
    # Test with missing prices
    result = total_value(inv, prices)
    expected = (10 * 0.5) + (5 * 0.3) + (3 * 0)  # orange has no price
    assert abs(result - expected) < 0.0001, f"Expected {expected}, got {result}"
    
    # Test with all prices present
    prices["orange"] = 0.2
    result = total_value(inv, prices)
    expected = (10 * 0.5) + (5 * 0.3) + (3 * 0.2)
    assert abs(result - expected) < 0.0001, f"Expected {expected}, got {result}"
    
    # Test with empty inventory
    result = total_value({}, prices)
    assert result == 0, f"Expected 0, got {result}"
    
    print("All total_value tests passed")


if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("\nAll comprehensive tests passed!")
