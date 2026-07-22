"""Test script for inventory module."""
from inventory import add_item, remove_item, total_value

def test_add_item():
    # Test basic addition
    inv = {}
    result = add_item(inv, "apple", 5)
    assert result == {"apple": 5}, f"Expected {{'apple': 5}}, got {result}"
    
    # Test accumulation (this is the bug)
    inv = {"apple": 3}
    result = add_item(inv, "apple", 2)
    assert result == {"apple": 5}, f"Expected {{'apple': 5}} after accumulation, got {result}"
    
    # Test negative qty raises ValueError
    try:
        add_item({}, "apple", -1)
        assert False, "Should have raised ValueError for negative qty"
    except ValueError:
        pass
    
    print("add_item tests passed!")

def test_remove_item():
    # Test basic removal
    inv = {"apple": 5}
    result = remove_item(inv, "apple", 3)
    assert result == {"apple": 2}, f"Expected {{'apple': 2}}, got {result}"
    
    # Test deletion when reaching 0
    inv = {"apple": 5}
    result = remove_item(inv, "apple", 5)
    assert result == {}, f"Expected {{}} after removal to 0, got {result}"
    
    # Test unknown name raises KeyError
    try:
        remove_item({}, "apple", 1)
        assert False, "Should have raised KeyError for unknown item"
    except KeyError:
        pass
    
    # Test removing more than available raises ValueError
    try:
        remove_item({"apple": 2}, "apple", 5)
        assert False, "Should have raised ValueError for over-removal"
    except ValueError:
        pass
    
    print("remove_item tests passed!")

def test_total_value():
    # Test basic calculation
    inv = {"apple": 3}
    prices = {"apple": 2.5}
    result = total_value(inv, prices)
    assert result == 7.5, f"Expected 7.5, got {result}"
    
    # Test missing price counts as 0 (this is the bug)
    inv = {"apple": 3, "banana": 2}
    prices = {"apple": 2.5}  # banana is missing
    result = total_value(inv, prices)
    assert result == 7.5, f"Expected 7.5 (banana counts as 0), got {result}"
    
    print("total_value tests passed!")

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("\nAll tests passed!")
