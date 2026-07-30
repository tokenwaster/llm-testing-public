#!/usr/bin/env python3
"""Test script to verify inventory.py matches spec."""

import inventory

def test_add_item():
    print("Testing add_item...")
    inv = {}
    # Test basic add
    result = inventory.add_item(inv, "apple", 5)
    assert result == {"apple": 5}, f"Expected {{'apple': 5}}, got {result}"
    assert result is inv, "Should return the same dict"
    
    # Test accumulate
    result = inventory.add_item(inv, "apple", 3)
    assert result == {"apple": 8}, f"Expected {{'apple': 8}}, got {result}"
    
    # Test negative qty raises
    try:
        inventory.add_item(inv, "apple", -1)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("  add_item: PASS")

def test_remove_item():
    print("Testing remove_item...")
    inv = {"apple": 5}
    
    # Test basic remove
    result = inventory.remove_item(inv, "apple", 2)
    assert result == {"apple": 3}, f"Expected {{'apple': 3}}, got {result}"
    
    # Test remove to zero deletes key
    result = inventory.remove_item(inv, "apple", 3)
    assert result == {}, f"Expected {{}}, got {result}"
    
    # Test unknown name raises KeyError
    try:
        inventory.remove_item(inv, "banana", 1)
        assert False, "Should have raised KeyError"
    except KeyError:
        pass
    
    # Test removing more than available raises ValueError
    inv = {"apple": 5}
    try:
        inventory.remove_item(inv, "apple", 10)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("  remove_item: PASS")

def test_total_value():
    print("Testing total_value...")
    inv = {"apple": 5, "banana": 3}
    prices = {"apple": 1.5, "banana": 2.0}
    
    # Test normal case
    result = inventory.total_value(inv, prices)
    assert result == 5*1.5 + 3*2.0, f"Expected {5*1.5 + 3*2.0}, got {result}"
    
    # Test missing price counts as 0
    inv2 = {"apple": 5, "orange": 10}
    prices2 = {"apple": 1.5}
    result = inventory.total_value(inv2, prices2)
    assert result == 5*1.5, f"Expected {5*1.5}, got {result}"
    
    # Test empty inventory
    result = inventory.total_value({}, prices)
    assert result == 0, f"Expected 0, got {result}"
    
    print("  total_value: PASS")

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("\nAll tests passed!")